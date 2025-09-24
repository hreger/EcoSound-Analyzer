# Database Handler for EcoSound Analyzer
import sqlite3
import json
from datetime import datetime, timedelta
import os
from contextlib import contextmanager

class DatabaseHandler:
    """Handle database operations for EcoSound Analyzer"""
    
    def __init__(self, db_path='ecosound.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Audio recordings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS recordings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT,
                    latitude REAL,
                    longitude REAL,
                    timestamp TEXT,
                    noise_level REAL,
                    classification TEXT,
                    anomaly TEXT,
                    features TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Feedback table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    feedback_text TEXT NOT NULL,
                    latitude REAL,
                    longitude REAL,
                    noise_level REAL,
                    timestamp TEXT,
                    analysis TEXT,
                    status TEXT DEFAULT 'submitted',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Predictions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    latitude REAL,
                    longitude REAL,
                    predicted_db REAL,
                    confidence REAL,
                    weather_conditions TEXT,
                    timestamp TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # System calibration table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS calibrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT,
                    calibration_offset REAL,
                    reference_level REAL,
                    measured_level REAL,
                    timestamp TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """Get database connection with context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
        try:
            yield conn
        finally:
            conn.close()
    
    def save_audio_metadata(self, metadata):
        """Save audio recording metadata to database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO recordings 
                    (filename, latitude, longitude, timestamp, noise_level, classification, anomaly, features)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    metadata.get('filename'),
                    metadata.get('latitude'),
                    metadata.get('longitude'),
                    metadata.get('timestamp'),
                    metadata.get('noise_level'),
                    json.dumps(metadata.get('classification', [])),
                    json.dumps(metadata.get('anomaly', {})),
                    json.dumps(metadata.get('features', {}))
                ))
                
                conn.commit()
                return cursor.lastrowid
                
        except Exception as e:
            print(f"Error saving audio metadata: {e}")
            return None
    
    def save_feedback(self, feedback_entry):
        """Save citizen feedback to database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO feedback 
                    (feedback_text, latitude, longitude, noise_level, timestamp, analysis, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    feedback_entry.get('feedback'),
                    feedback_entry.get('latitude'),
                    feedback_entry.get('longitude'),
                    feedback_entry.get('noise_level'),
                    feedback_entry.get('timestamp'),
                    json.dumps(feedback_entry.get('analysis', {})),
                    feedback_entry.get('status', 'submitted')
                ))
                
                conn.commit()
                return cursor.lastrowid
                
        except Exception as e:
            print(f"Error saving feedback: {e}")
            return None
    
    def get_feedback_stats(self):
        """Get feedback statistics"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Total feedback count
                cursor.execute('SELECT COUNT(*) as total FROM feedback')
                total = cursor.fetchone()['total']
                
                # Recent feedback (last 24 hours)
                yesterday = (datetime.now() - timedelta(days=1)).isoformat()
                cursor.execute('SELECT COUNT(*) as recent FROM feedback WHERE created_at > ?', (yesterday,))
                recent = cursor.fetchone()['recent']
                
                # Average noise level
                cursor.execute('SELECT AVG(noise_level) as avg_noise FROM feedback WHERE noise_level IS NOT NULL')
                avg_noise = cursor.fetchone()['avg_noise'] or 0
                
                # Top noise sources from analysis
                cursor.execute('SELECT analysis FROM feedback WHERE analysis IS NOT NULL')
                analyses = cursor.fetchall()
                
                source_counts = {}
                urgent_count = 0
                
                for row in analyses:
                    try:
                        analysis = json.loads(row['analysis'])
                        sources = analysis.get('noise_sources', [])
                        for source in sources:
                            source_counts[source] = source_counts.get(source, 0) + 1
                        
                        if analysis.get('urgency') == 'high':
                            urgent_count += 1
                    except:
                        continue
                
                # Top sources
                top_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                
                return {
                    'total': total,
                    'recent': recent,
                    'sources': [{'source': source, 'count': count} for source, count in top_sources],
                    'urgent': urgent_count,
                    'avg_noise': round(avg_noise, 1)
                }
                
        except Exception as e:
            print(f"Error getting feedback stats: {e}")
            return {}
    
    def get_historical_data(self, latitude, longitude, days=30, radius_km=1.0):
        """Get historical noise data for a location"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Simple radius-based filtering (in production, use proper geographic queries)
                lat_range = radius_km / 111.0  # Approximate degrees per km
                lng_range = radius_km / (111.0 * abs(latitude) if latitude else 111.0)
                
                since_date = (datetime.now() - timedelta(days=days)).isoformat()
                
                cursor.execute('''
                    SELECT timestamp, noise_level, classification 
                    FROM recordings 
                    WHERE latitude BETWEEN ? AND ? 
                    AND longitude BETWEEN ? AND ?
                    AND created_at > ?
                    AND noise_level IS NOT NULL
                    ORDER BY timestamp DESC
                ''', (
                    latitude - lat_range, latitude + lat_range,
                    longitude - lng_range, longitude + lng_range,
                    since_date
                ))
                
                results = []
                for row in cursor.fetchall():
                    try:
                        timestamp = datetime.fromisoformat(row['timestamp'])
                        results.append({
                            'timestamp': row['timestamp'],
                            'noise_level': row['noise_level'],
                            'hour': timestamp.hour,
                            'day_of_week': timestamp.weekday(),
                            'classification': json.loads(row['classification']) if row['classification'] else []
                        })
                    except:
                        continue
                
                return results
                
        except Exception as e:
            print(f"Error getting historical data: {e}")
            return []
    
    def save_prediction(self, prediction_data):
        """Save noise prediction to database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO predictions 
                    (latitude, longitude, predicted_db, confidence, weather_conditions, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    prediction_data.get('latitude'),
                    prediction_data.get('longitude'),
                    prediction_data.get('predicted_db'),
                    prediction_data.get('confidence'),
                    prediction_data.get('weather_conditions'),
                    prediction_data.get('timestamp')
                ))
                
                conn.commit()
                return cursor.lastrowid
                
        except Exception as e:
            print(f"Error saving prediction: {e}")
            return None
    
    def get_noise_hotspots(self, threshold_db=70, days=7):
        """Get noise pollution hotspots"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                since_date = (datetime.now() - timedelta(days=days)).isoformat()
                
                cursor.execute('''
                    SELECT 
                        latitude, 
                        longitude, 
                        AVG(noise_level) as avg_db,
                        MAX(noise_level) as peak_db,
                        COUNT(*) as measurement_count
                    FROM recordings 
                    WHERE noise_level >= ? 
                    AND created_at > ?
                    AND latitude IS NOT NULL 
                    AND longitude IS NOT NULL
                    GROUP BY 
                        ROUND(latitude, 3), 
                        ROUND(longitude, 3)
                    HAVING COUNT(*) >= 3
                    ORDER BY avg_db DESC
                    LIMIT 20
                ''', (threshold_db, since_date))
                
                hotspots = []
                for i, row in enumerate(cursor.fetchall()):
                    severity = 'critical' if row['avg_db'] >= 80 else 'high' if row['avg_db'] >= 70 else 'medium'
                    
                    hotspots.append({
                        'id': i + 1,
                        'location': {
                            'latitude': row['latitude'],
                            'longitude': row['longitude']
                        },
                        'average_db': round(row['avg_db'], 1),
                        'peak_db': round(row['peak_db'], 1),
                        'severity': severity,
                        'measurement_count': row['measurement_count'],
                        'area_description': f"Area near {row['latitude']:.3f}, {row['longitude']:.3f}"
                    })
                
                return hotspots
                
        except Exception as e:
            print(f"Error getting hotspots: {e}")
            return []
    
    def save_calibration(self, calibration_data):
        """Save system calibration data"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO calibrations 
                    (device_id, calibration_offset, reference_level, measured_level, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    calibration_data.get('device_id'),
                    calibration_data.get('calibration_offset'),
                    calibration_data.get('reference_level'),
                    calibration_data.get('measured_level'),
                    calibration_data.get('timestamp')
                ))
                
                conn.commit()
                return cursor.lastrowid
                
        except Exception as e:
            print(f"Error saving calibration: {e}")
            return None
    
    def get_recent_recordings(self, limit=50):
        """Get recent audio recordings"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM recordings 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (limit,))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'id': row['id'],
                        'filename': row['filename'],
                        'latitude': row['latitude'],
                        'longitude': row['longitude'],
                        'timestamp': row['timestamp'],
                        'noise_level': row['noise_level'],
                        'classification': json.loads(row['classification']) if row['classification'] else [],
                        'anomaly': json.loads(row['anomaly']) if row['anomaly'] else {},
                        'created_at': row['created_at']
                    })
                
                return results
                
        except Exception as e:
            print(f"Error getting recent recordings: {e}")
            return []
    
    def clean_old_data(self, days_to_keep=90):
        """Clean old data from database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
                
                # Clean old recordings
                cursor.execute('DELETE FROM recordings WHERE created_at < ?', (cutoff_date,))
                recordings_deleted = cursor.rowcount
                
                # Clean old feedback
                cursor.execute('DELETE FROM feedback WHERE created_at < ?', (cutoff_date,))
                feedback_deleted = cursor.rowcount
                
                # Clean old predictions
                cursor.execute('DELETE FROM predictions WHERE created_at < ?', (cutoff_date,))
                predictions_deleted = cursor.rowcount
                
                conn.commit()
                
                return {
                    'recordings_deleted': recordings_deleted,
                    'feedback_deleted': feedback_deleted,
                    'predictions_deleted': predictions_deleted
                }
                
        except Exception as e:
            print(f"Error cleaning old data: {e}")
            return {}
    
    def get_database_stats(self):
        """Get database statistics"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Table counts
                for table in ['recordings', 'feedback', 'predictions', 'calibrations']:
                    cursor.execute(f'SELECT COUNT(*) as count FROM {table}')
                    stats[f'{table}_count'] = cursor.fetchone()['count']
                
                # Database file size
                if os.path.exists(self.db_path):
                    stats['db_size_mb'] = round(os.path.getsize(self.db_path) / (1024 * 1024), 2)
                else:
                    stats['db_size_mb'] = 0
                
                return stats
                
        except Exception as e:
            print(f"Error getting database stats: {e}")
            return {}

# Global database handler instance
db_handler = DatabaseHandler()

# Convenience functions for external use
def save_audio_metadata(metadata):
    return db_handler.save_audio_metadata(metadata)

def save_feedback(feedback_entry):
    return db_handler.save_feedback(feedback_entry)

def get_feedback_stats():
    return db_handler.get_feedback_stats()

def get_historical_data(latitude, longitude, days=30):
    return db_handler.get_historical_data(latitude, longitude, days)