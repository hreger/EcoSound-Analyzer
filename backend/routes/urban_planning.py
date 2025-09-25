# Enhanced Urban Planning API Routes
# backend/routes/urban_planning.py

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import json
import sqlite3
from utils.db_handler import DatabaseHandler
from utils.zoning_analysis import ZoningAnalyzer
from utils.infrastructure_planner import BangaloreInfrastructurePlanner

urban_planning_bp = Blueprint('urban_planning', __name__)
db = DatabaseHandler()

@urban_planning_bp.route('/zoning/analysis', methods=['POST'])
def analyze_zoning_compliance():
    """Analyze noise levels against zoning regulations"""
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    zone_type = data.get('zone_type')  # residential, commercial, industrial, mixed
    
    # Get historical noise data for the area
    historical_data = db.get_area_noise_data(latitude, longitude, radius_km=0.5, days=30)
    
    analyzer = ZoningAnalyzer()
    compliance_report = analyzer.assess_zoning_compliance(
        historical_data, zone_type, latitude, longitude
    )
    
    return jsonify({
        'zone_type': zone_type,
        'compliance_status': compliance_report['status'],
        'violations': compliance_report['violations'],
        'recommendations': compliance_report['recommendations'],
        'risk_score': compliance_report['risk_score'],
        'peak_violation_hours': compliance_report['peak_hours']
    })

@urban_planning_bp.route('/hotspots/advanced', methods=['GET'])
def get_advanced_hotspots():
    """Get detailed noise hotspots with urban planning context"""
    threshold_db = request.args.get('threshold', 65, type=float)
    radius_km = request.args.get('radius', 2.0, type=float)
    days = request.args.get('days', 7, type=int)
    zone_filter = request.args.get('zone_type', None)
    
    hotspots = db.get_advanced_hotspots(
        threshold_db=threshold_db,
        radius_km=radius_km,
        days=days,
        zone_filter=zone_filter
    )
    
    # Enrich with urban planning data
    enriched_hotspots = []
    for hotspot in hotspots:
        planner = InfrastructurePlanner()
        planning_context = planner.get_planning_context(
            hotspot['latitude'], hotspot['longitude']
        )
        
        enriched_hotspots.append({
            **hotspot,
            'zoning_info': planning_context['zoning'],
            'nearby_infrastructure': planning_context['infrastructure'],
            'green_space_distance': planning_context['green_space_distance'],
            'population_density': planning_context['population_density'],
            'mitigation_priority': planning_context['mitigation_priority'],
            'suggested_interventions': planning_context['interventions']
        })
    
    return jsonify({
        'hotspots': enriched_hotspots,
        'summary': {
            'total_hotspots': len(enriched_hotspots),
            'high_priority': len([h for h in enriched_hotspots if h['mitigation_priority'] == 'high']),
            'zone_distribution': _get_zone_distribution(enriched_hotspots)
        }
    })

@urban_planning_bp.route('/green-space/recommendations', methods=['POST'])
def recommend_green_spaces():
    """Recommend green space locations for noise mitigation"""
    data = request.get_json()
    area_bounds = data.get('bounds')  # {'north': lat, 'south': lat, 'east': lng, 'west': lng}
    budget = data.get('budget', 1000000)  # Budget in currency units
    
    planner = InfrastructurePlanner()
    recommendations = planner.recommend_green_spaces(area_bounds, budget)
    
    return jsonify({
        'recommendations': recommendations,
        'total_cost': sum(r['estimated_cost'] for r in recommendations),
        'noise_reduction_potential': sum(r['noise_reduction_db'] for r in recommendations),
        'affected_population': sum(r['beneficiary_population'] for r in recommendations)
    })

@urban_planning_bp.route('/infrastructure/impact-assessment', methods=['POST'])
def assess_infrastructure_impact():
    """Assess noise impact of proposed infrastructure"""
    data = request.get_json()
    infrastructure_type = data.get('type')  # road, construction, industrial
    location = data.get('location')
    duration = data.get('duration_months', 12)
    
    planner = InfrastructurePlanner()
    impact_assessment = planner.assess_infrastructure_impact(
        infrastructure_type, location, duration
    )
    
    return jsonify({
        'impact_assessment': impact_assessment,
        'affected_zones': impact_assessment['affected_zones'],
        'mitigation_measures': impact_assessment['required_mitigations'],
        'compliance_risk': impact_assessment['compliance_risk'],
        'estimated_complaints': impact_assessment['complaint_forecast']
    })

def _get_zone_distribution(hotspots):
    """Helper to calculate zone distribution"""
    zones = {}
    for hotspot in hotspots:
        zone = hotspot.get('zoning_info', {}).get('primary_zone', 'unknown')
        zones[zone] = zones.get(zone, 0) + 1
    return zones