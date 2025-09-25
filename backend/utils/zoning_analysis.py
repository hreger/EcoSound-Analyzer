# Zoning Analysis for Urban Planning
# backend/utils/zoning_analysis.py

import numpy as np
from datetime import datetime, timedelta
import json

class ZoningAnalyzer:
    """Analyze noise compliance with zoning regulations"""
    
    def __init__(self):
        # Define noise limits by zone type (dB) based on local regulations
        self.zone_limits = {
            'residential': {
                'day': 55,     # 6 AM - 10 PM
                'night': 45,   # 10 PM - 6 AM
                'critical': 65  # Never exceed
            },
            'commercial': {
                'day': 65,
                'night': 55,
                'critical': 75
            },
            'industrial': {
                'day': 70,
                'night': 60,
                'critical': 80
            },
            'mixed': {
                'day': 60,
                'night': 50,
                'critical': 70
            },
            'educational': {
                'day': 50,     # Schools need quieter environment
                'night': 45,
                'critical': 60
            },
            'hospital': {
                'day': 45,     # Hospitals need very quiet
                'night': 40,
                'critical': 55
            }
        }
    
    def assess_zoning_compliance(self, historical_data, zone_type, latitude, longitude):
        """Assess compliance with zoning noise regulations"""
        
        if zone_type not in self.zone_limits:
            zone_type = 'residential'  # Default fallback
        
        limits = self.zone_limits[zone_type]
        violations = []
        compliance_score = 100
        
        # Analyze historical data
        for record in historical_data:
            timestamp = datetime.fromisoformat(record['timestamp'])
            noise_level = record['noise_level']
            hour = timestamp.hour
            
            # Determine time period
            is_night = hour >= 22 or hour <= 6
            applicable_limit = limits['night'] if is_night else limits['day']
            
            # Check violations
            if noise_level > limits['critical']:
                violations.append({
                    'type': 'critical',
                    'timestamp': record['timestamp'],
                    'measured_db': noise_level,
                    'limit_db': limits['critical'],
                    'excess_db': noise_level - limits['critical'],
                    'severity': 'high'
                })
                compliance_score -= 10
                
            elif noise_level > applicable_limit:
                violations.append({
                    'type': 'period_violation',
                    'timestamp': record['timestamp'],
                    'measured_db': noise_level,
                    'limit_db': applicable_limit,
                    'excess_db': noise_level - applicable_limit,
                    'severity': 'medium' if noise_level > applicable_limit + 5 else 'low',
                    'period': 'night' if is_night else 'day'
                })
                compliance_score -= 2 if is_night else 1
        
        # Generate recommendations
        recommendations = self._generate_recommendations(violations, zone_type, limits)
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(violations, len(historical_data))
        
        # Find peak violation hours
        peak_hours = self._find_peak_violation_hours(violations)
        
        return {
            'status': 'compliant' if compliance_score >= 80 else 'non_compliant',
            'compliance_score': max(0, compliance_score),
            'violations': violations,
            'total_violations': len(violations),
            'recommendations': recommendations,
            'risk_score': risk_score,
            'peak_hours': peak_hours,
            'zone_limits': limits
        }
    
    def _generate_recommendations(self, violations, zone_type, limits):
        """Generate actionable recommendations based on violations"""
        recommendations = []
        
        # Count violation types
        critical_violations = len([v for v in violations if v['type'] == 'critical'])
        night_violations = len([v for v in violations if v.get('period') == 'night'])
        day_violations = len([v for v in violations if v.get('period') == 'day'])
        
        if critical_violations > 0:
            recommendations.append({
                'priority': 'high',
                'category': 'immediate_action',
                'title': 'Critical Noise Level Violations',
                'description': f'{critical_violations} instances exceeded critical limit of {limits["critical"]} dB',
                'actions': [
                    'Immediate noise source investigation required',
                    'Consider temporary noise barriers',
                    'Implement 24/7 noise monitoring',
                    'Issue noise citations if applicable'
                ]
            })
        
        if night_violations > day_violations and night_violations > 5:
            recommendations.append({
                'priority': 'high',
                'category': 'nighttime_mitigation',
                'title': 'Excessive Nighttime Noise',
                'description': f'{night_violations} nighttime violations (limit: {limits["night"]} dB)',
                'actions': [
                    'Enforce stricter nighttime noise ordinances',
                    'Install noise barriers along major roads',
                    'Restrict heavy vehicle traffic during night hours',
                    'Consider rezoning if violations persist'
                ]
            })
        
        if zone_type == 'residential' and day_violations > 10:
            recommendations.append({
                'priority': 'medium',
                'category': 'green_infrastructure',
                'title': 'Green Space Noise Mitigation',
                'description': 'Multiple daytime violations in residential zone',
                'actions': [
                    'Plant noise-absorbing vegetation barriers',
                    'Create buffer zones with parks/green spaces',
                    'Install acoustic fencing where appropriate',
                    'Consider traffic calming measures'
                ]
            })
        
        if len(violations) > 20:
            recommendations.append({
                'priority': 'medium',
                'category': 'infrastructure',
                'title': 'Infrastructure Improvements',
                'description': 'High frequency of noise violations indicates systemic issues',
                'actions': [
                    'Conduct comprehensive noise source mapping',
                    'Evaluate road surface improvements (quieter asphalt)',
                    'Optimize traffic signal timing to reduce stop/start noise',
                    'Consider alternative transportation options'
                ]
            })
        
        return recommendations
    
    def _calculate_risk_score(self, violations, total_measurements):
        """Calculate risk score (0-100) based on violation frequency and severity"""
        if total_measurements == 0:
            return 0
        
        violation_rate = len(violations) / total_measurements
        
        # Weight by severity
        severity_weights = {'high': 3, 'medium': 2, 'low': 1}
        weighted_violations = sum(severity_weights.get(v.get('severity', 'low'), 1) for v in violations)
        
        risk_score = min(100, (violation_rate * 100) + (weighted_violations / total_measurements * 50))
        return round(risk_score, 1)
    
    def _find_peak_violation_hours(self, violations):
        """Find hours with most violations"""
        hour_counts = {}
        for violation in violations:
            timestamp = datetime.fromisoformat(violation['timestamp'])
            hour = timestamp.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        # Return top 3 peak hours
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
        return [{'hour': hour, 'violations': count} for hour, count in sorted_hours[:3]]
    
    def get_zoning_recommendations_for_area(self, area_data):
        """Recommend optimal zoning based on noise patterns"""
        avg_day_noise = np.mean([d['noise_level'] for d in area_data if 6 <= datetime.fromisoformat(d['timestamp']).hour <= 22])
        avg_night_noise = np.mean([d['noise_level'] for d in area_data if datetime.fromisoformat(d['timestamp']).hour >= 22 or datetime.fromisoformat(d['timestamp']).hour <= 6])
        
        recommendations = []
        
        if avg_day_noise <= 50 and avg_night_noise <= 40:
            recommendations.append({
                'zone_type': 'residential',
                'suitability': 'high',
                'reason': 'Low noise levels suitable for residential development'
            })
        
        if 50 <= avg_day_noise <= 65:
            recommendations.append({
                'zone_type': 'mixed',
                'suitability': 'medium',
                'reason': 'Moderate noise levels suitable for mixed-use development'
            })
        
        if avg_day_noise >= 65:
            recommendations.append({
                'zone_type': 'commercial',
                'suitability': 'high',
                'reason': 'Higher noise levels appropriate for commercial/industrial use'
            })
        
        return recommendations