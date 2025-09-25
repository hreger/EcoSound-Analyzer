# Infrastructure Planning for Bangalore Urban Development
# backend/utils/infrastructure_planner.py

import numpy as np
import json
from geopy.distance import geodesic
from datetime import datetime, timedelta

class BangaloreInfrastructurePlanner:
    """Infrastructure planning specifically for Bangalore city"""
    
    def __init__(self):
        # Bangalore-specific zoning and landmarks
        self.bangalore_zones = {
            'cbd': {
                'center': (12.9716, 77.5946),  # MG Road area
                'radius_km': 3,
                'type': 'commercial',
                'noise_tolerance': 'high'
            },
            'koramangala': {
                'center': (12.9352, 77.6245),
                'radius_km': 2,
                'type': 'mixed',
                'noise_tolerance': 'medium'
            },
            'indiranagar': {
                'center': (12.9719, 77.6412),
                'radius_km': 2,
                'type': 'residential_commercial',
                'noise_tolerance': 'medium'
            },
            'whitefield': {
                'center': (12.9698, 77.7500),
                'radius_km': 4,
                'type': 'it_corridor',
                'noise_tolerance': 'medium'
            },
            'electronic_city': {
                'center': (12.8456, 77.6603),
                'radius_km': 3,
                'type': 'it_industrial',
                'noise_tolerance': 'high'
            },
            'malleswaram': {
                'center': (13.0033, 77.5811),
                'radius_km': 1.5,
                'type': 'residential',
                'noise_tolerance': 'low'
            },
            'jayanagar': {
                'center': (12.9279, 77.5970),
                'radius_km': 2,
                'type': 'residential',
                'noise_tolerance': 'low'
            }
        }
        
        # Major roads and infrastructure in Bangalore
        self.major_roads = [
            {'name': 'Outer Ring Road', 'coordinates': [(12.8200, 77.5900), (13.0800, 77.7200)], 'noise_impact': 'high'},
            {'name': 'Hosur Road', 'coordinates': [(12.9716, 77.5946), (12.8456, 77.6603)], 'noise_impact': 'high'},
            {'name': 'Bannerghatta Road', 'coordinates': [(12.9352, 77.6245), (12.8800, 77.6000)], 'noise_impact': 'medium'},
            {'name': 'Whitefield Road', 'coordinates': [(12.9719, 77.6412), (12.9698, 77.7500)], 'noise_impact': 'medium'},
            {'name': 'Mysore Road', 'coordinates': [(12.9716, 77.5946), (12.9000, 77.5200)], 'noise_impact': 'high'}
        ]
        
        # Green spaces in Bangalore
        self.existing_green_spaces = [
            {'name': 'Cubbon Park', 'center': (12.9762, 77.5993), 'area_hectares': 120, 'noise_reduction': 8},
            {'name': 'Lalbagh', 'center': (12.9507, 77.5848), 'area_hectares': 97, 'noise_reduction': 7},
            {'name': 'Bannerghatta National Park', 'center': (12.7980, 77.5779), 'area_hectares': 2618, 'noise_reduction': 12},
            {'name': 'Sankey Tank', 'center': (12.9896, 77.5615), 'area_hectares': 15, 'noise_reduction': 5},
            {'name': 'Ulsoor Lake', 'center': (12.9806, 77.6166), 'area_hectares': 50, 'noise_reduction': 6}
        ]
    
    def get_planning_context(self, latitude, longitude):
        """Get urban planning context for a specific location in Bangalore"""
        
        # Determine which zone this location belongs to
        zone_info = self._identify_zone(latitude, longitude)
        
        # Find nearby infrastructure
        nearby_infrastructure = self._find_nearby_infrastructure(latitude, longitude)
        
        # Calculate distance to nearest green space
        green_space_distance = self._calculate_green_space_distance(latitude, longitude)
        
        # Estimate population density (simplified model)
        population_density = self._estimate_population_density(latitude, longitude, zone_info)
        
        # Determine mitigation priority
        mitigation_priority = self._calculate_mitigation_priority(
            zone_info, nearby_infrastructure, green_space_distance, population_density
        )
        
        # Suggest interventions
        interventions = self._suggest_interventions(
            latitude, longitude, zone_info, nearby_infrastructure, green_space_distance
        )
        
        return {
            'zoning': zone_info,
            'infrastructure': nearby_infrastructure,
            'green_space_distance': green_space_distance,
            'population_density': population_density,
            'mitigation_priority': mitigation_priority,
            'interventions': interventions
        }
    
    def recommend_green_spaces_bangalore(self, area_bounds, budget):
        """Recommend green space locations specifically for Bangalore"""
        
        recommendations = []
        
        # High-priority areas for green space development in Bangalore
        priority_areas = [
            {
                'location': (12.9200, 77.6100),  # HSR Layout area
                'name': 'HSR Layout Green Corridor',
                'type': 'linear_park',
                'estimated_cost': 5000000,  # INR 50 lakhs
                'noise_reduction_db': 6,
                'beneficiary_population': 25000,
                'implementation_months': 8,
                'justification': 'High-density residential area with limited green cover'
            },
            {
                'location': (12.9950, 77.7050),  # Marathahalli area
                'name': 'Marathahalli Noise Buffer Park',
                'type': 'buffer_park',
                'estimated_cost': 8000000,  # INR 80 lakhs
                'noise_reduction_db': 8,
                'beneficiary_population': 35000,
                'implementation_months': 12,
                'justification': 'Major IT corridor with heavy traffic noise'
            },
            {
                'location': (12.8900, 77.6400),  # Bommanahalli area
                'name': 'Bommanahalli Urban Forest',
                'type': 'urban_forest',
                'estimated_cost': 12000000,  # INR 1.2 crores
                'noise_reduction_db': 10,
                'beneficiary_population': 50000,
                'implementation_months': 18,
                'justification': 'Growing residential area near Electronic City'
            },
            {
                'location': (13.0350, 77.5950),  # Hebbal area
                'name': 'Hebbal Lake Restoration & Noise Barrier',
                'type': 'lake_restoration',
                'estimated_cost': 15000000,  # INR 1.5 crores
                'noise_reduction_db': 12,
                'beneficiary_population': 40000,
                'implementation_months': 24,
                'justification': 'Major flyover noise impact mitigation'
            }
        ]
        
        # Filter by budget and area bounds
        feasible_recommendations = []
        remaining_budget = budget
        
        # Sort by cost-effectiveness (noise reduction per rupee)
        priority_areas.sort(key=lambda x: x['noise_reduction_db'] / (x['estimated_cost'] / 1000000), reverse=True)
        
        for area in priority_areas:
            if area['estimated_cost'] <= remaining_budget:
                # Check if within bounds
                lat, lng = area['location']
                if (area_bounds['south'] <= lat <= area_bounds['north'] and 
                    area_bounds['west'] <= lng <= area_bounds['east']):
                    
                    feasible_recommendations.append({
                        **area,
                        'priority_score': self._calculate_green_space_priority(area),
                        'environmental_benefits': {
                            'air_quality_improvement': area['noise_reduction_db'] * 0.8,
                            'temperature_reduction_celsius': area['noise_reduction_db'] * 0.3,
                            'biodiversity_score': area['noise_reduction_db'] * 2
                        }
                    })
                    remaining_budget -= area['estimated_cost']
        
        return feasible_recommendations
    
    def assess_infrastructure_impact_bangalore(self, infrastructure_type, location, duration_months):
        """Assess infrastructure impact specifically for Bangalore context"""
        
        lat, lng = location
        zone_info = self._identify_zone(lat, lng)
        
        # Bangalore-specific impact factors
        impact_factors = {
            'metro_construction': {
                'noise_increase_db': 15,
                'affected_radius_km': 0.8,
                'peak_hours': [(7, 10), (17, 20)],
                'mitigation_required': True
            },
            'flyover_construction': {
                'noise_increase_db': 20,
                'affected_radius_km': 1.2,
                'peak_hours': [(6, 18)],  # Daytime construction
                'mitigation_required': True
            },
            'road_widening': {
                'noise_increase_db': 12,
                'affected_radius_km': 0.5,
                'peak_hours': [(22, 6)],  # Often done at night
                'mitigation_required': True
            },
            'it_park_development': {
                'noise_increase_db': 8,
                'affected_radius_km': 1.0,
                'peak_hours': [(7, 10), (18, 21)],
                'mitigation_required': False
            }
        }
        
        if infrastructure_type not in impact_factors:
            infrastructure_type = 'road_widening'  # Default
        
        impact = impact_factors[infrastructure_type]
        
        # Calculate affected zones
        affected_zones = []
        for zone_name, zone_data in self.bangalore_zones.items():
            distance = geodesic(location, zone_data['center']).kilometers
            if distance <= impact['affected_radius_km']:
                affected_zones.append({
                    'zone': zone_name,
                    'type': zone_data['type'],
                    'distance_km': round(distance, 2),
                    'impact_severity': 'high' if distance < impact['affected_radius_km'] * 0.5 else 'medium'
                })
        
        # Generate Bangalore-specific mitigation measures
        mitigation_measures = self._generate_bangalore_mitigations(
            infrastructure_type, zone_info, affected_zones, impact
        )
        
        # Calculate compliance risk
        compliance_risk = self._calculate_compliance_risk_bangalore(
            zone_info, impact['noise_increase_db'], duration_months
        )
        
        # Estimate complaints based on Bangalore patterns
        complaint_forecast = self._estimate_complaints_bangalore(
            affected_zones, impact, duration_months
        )
        
        return {
            'infrastructure_type': infrastructure_type,
            'location': location,
            'duration_months': duration_months,
            'noise_impact': impact,
            'affected_zones': affected_zones,
            'required_mitigations': mitigation_measures,
            'compliance_risk': compliance_risk,
            'complaint_forecast': complaint_forecast,
            'monitoring_requirements': {
                'continuous_monitoring': True,
                'reporting_frequency': 'weekly',
                'community_engagement': True
            }
        }
    
    def _identify_zone(self, latitude, longitude):
        """Identify which Bangalore zone a location belongs to"""
        min_distance = float('inf')
        closest_zone = None
        
        for zone_name, zone_data in self.bangalore_zones.items():
            distance = geodesic((latitude, longitude), zone_data['center']).kilometers
            if distance <= zone_data['radius_km'] and distance < min_distance:
                min_distance = distance
                closest_zone = {
                    'name': zone_name,
                    'type': zone_data['type'],
                    'noise_tolerance': zone_data['noise_tolerance'],
                    'distance_from_center': round(distance, 2)
                }
        
        if not closest_zone:
            closest_zone = {
                'name': 'peripheral',
                'type': 'mixed',
                'noise_tolerance': 'medium',
                'distance_from_center': min_distance
            }
        
        return closest_zone
    
    def _find_nearby_infrastructure(self, latitude, longitude):
        """Find nearby major infrastructure"""
        nearby = []
        
        for road in self.major_roads:
            # Simplified distance calculation to road
            min_distance = min(
                geodesic((latitude, longitude), coord).kilometers 
                for coord in road['coordinates']
            )
            
            if min_distance <= 2.0:  # Within 2km
                nearby.append({
                    'type': 'major_road',
                    'name': road['name'],
                    'distance_km': round(min_distance, 2),
                    'noise_impact': road['noise_impact']
                })
        
        return nearby
    
    def _calculate_green_space_distance(self, latitude, longitude):
        """Calculate distance to nearest green space"""
        min_distance = float('inf')
        nearest_green_space = None
        
        for green_space in self.existing_green_spaces:
            distance = geodesic((latitude, longitude), green_space['center']).kilometers
            if distance < min_distance:
                min_distance = distance
                nearest_green_space = green_space['name']
        
        return {
            'distance_km': round(min_distance, 2),
            'nearest_green_space': nearest_green_space,
            'adequacy': 'adequate' if min_distance <= 1.0 else 'inadequate'
        }
    
    def _estimate_population_density(self, latitude, longitude, zone_info):
        """Estimate population density based on zone type"""
        density_map = {
            'residential': 15000,  # people per sq km
            'commercial': 25000,
            'mixed': 20000,
            'it_corridor': 18000,
            'it_industrial': 12000,
            'residential_commercial': 22000
        }
        
        base_density = density_map.get(zone_info['type'], 15000)
        
        # Adjust based on distance from zone center
        distance_factor = max(0.5, 1 - (zone_info['distance_from_center'] / 5))
        
        return round(base_density * distance_factor)
    
    def _calculate_mitigation_priority(self, zone_info, infrastructure, green_space, population_density):
        """Calculate mitigation priority"""
        priority_score = 0
        
        # Zone type factor
        if zone_info['noise_tolerance'] == 'low':
            priority_score += 3
        elif zone_info['noise_tolerance'] == 'medium':
            priority_score += 2
        else:
            priority_score += 1
        
        # Infrastructure proximity
        high_impact_roads = len([i for i in infrastructure if i['noise_impact'] == 'high'])
        priority_score += high_impact_roads * 2
        
        # Green space adequacy
        if green_space['adequacy'] == 'inadequate':
            priority_score += 2
        
        # Population density
        if population_density > 20000:
            priority_score += 2
        elif population_density > 15000:
            priority_score += 1
        
        if priority_score >= 6:
            return 'high'
        elif priority_score >= 3:
            return 'medium'
        else:
            return 'low'
    
    def _suggest_interventions(self, latitude, longitude, zone_info, infrastructure, green_space):
        """Suggest specific interventions for Bangalore context"""
        interventions = []
        
        # High-impact road nearby
        high_impact_roads = [i for i in infrastructure if i['noise_impact'] == 'high']
        if high_impact_roads:
            interventions.append({
                'type': 'noise_barrier',
                'description': f'Install acoustic barriers along {high_impact_roads[0]["name"]}',
                'estimated_cost_inr': 2000000,  # 20 lakhs per km
                'noise_reduction_db': 8,
                'implementation_months': 6
            })
        
        # Inadequate green space
        if green_space['adequacy'] == 'inadequate':
            interventions.append({
                'type': 'green_buffer',
                'description': 'Create green buffer zone with native trees',
                'estimated_cost_inr': 1500000,  # 15 lakhs
                'noise_reduction_db': 5,
                'implementation_months': 8
            })
        
        # Residential area with medium/high priority
        if zone_info['type'] in ['residential', 'mixed'] and zone_info['noise_tolerance'] == 'low':
            interventions.append({
                'type': 'traffic_calming',
                'description': 'Implement speed bumps and traffic signals optimization',
                'estimated_cost_inr': 500000,  # 5 lakhs
                'noise_reduction_db': 3,
                'implementation_months': 2
            })
        
        return interventions
    
    def _calculate_green_space_priority(self, area):
        """Calculate priority score for green space development"""
        # Cost-effectiveness score
        effectiveness = area['noise_reduction_db'] / (area['estimated_cost'] / 1000000)
        
        # Population benefit score
        population_benefit = area['beneficiary_population'] / 10000
        
        return round(effectiveness + population_benefit, 2)
    
    def _generate_bangalore_mitigations(self, infrastructure_type, zone_info, affected_zones, impact):
        """Generate Bangalore-specific mitigation measures"""
        mitigations = []
        
        # Standard measures for all construction
        mitigations.extend([
            'Install temporary noise barriers (minimum 3m height)',
            'Restrict construction to daytime hours (7 AM - 7 PM)',
            'Use quieter construction equipment where possible',
            'Implement dust suppression to reduce secondary noise'
        ])
        
        # Zone-specific measures
        residential_zones = [z for z in affected_zones if 'residential' in z['type']]
        if residential_zones:
            mitigations.extend([
                'Provide prior notice to residents (minimum 7 days)',
                'Establish community liaison for complaints',
                'Install real-time noise monitoring displays'
            ])
        
        # Infrastructure-specific measures
        if infrastructure_type == 'metro_construction':
            mitigations.extend([
                'Use tunnel boring machines for underground sections',
                'Install vibration monitoring systems',
                'Coordinate with BMRCL noise guidelines'
            ])
        
        if infrastructure_type == 'flyover_construction':
            mitigations.extend([
                'Pre-cast construction elements off-site',
                'Use rubber-tired equipment instead of steel-tracked',
                'Install permanent noise barriers as construction progresses'
            ])
        
        return mitigations
    
    def _calculate_compliance_risk_bangalore(self, zone_info, noise_increase, duration_months):
        """Calculate compliance risk specific to Bangalore regulations"""
        base_risk = 'low'
        
        # Karnataka State Pollution Control Board limits
        if zone_info['noise_tolerance'] == 'low' and noise_increase > 10:
            base_risk = 'high'
        elif zone_info['noise_tolerance'] == 'medium' and noise_increase > 15:
            base_risk = 'high'
        elif noise_increase > 20:
            base_risk = 'high'
        elif noise_increase > 8:
            base_risk = 'medium'
        
        # Duration factor
        if duration_months > 12:
            if base_risk == 'medium':
                base_risk = 'high'
            elif base_risk == 'low':
                base_risk = 'medium'
        
        return base_risk
    
    def _estimate_complaints_bangalore(self, affected_zones, impact, duration_months):
        """Estimate complaints based on Bangalore patterns"""
        # Base complaint rate per 1000 people per month
        complaint_rates = {
            'residential': 5,
            'mixed': 3,
            'commercial': 1,
            'it_corridor': 2
        }
        
        total_estimated_complaints = 0
        
        for zone in affected_zones:
            zone_type = zone['type']
            base_rate = complaint_rates.get(zone_type, 2)
            
            # Adjust for impact severity
            if zone['impact_severity'] == 'high':
                adjusted_rate = base_rate * 2
            else:
                adjusted_rate = base_rate
            
            # Estimate population in affected area (simplified)
            estimated_population = 5000  # Rough estimate per zone
            
            monthly_complaints = (estimated_population / 1000) * adjusted_rate
            total_estimated_complaints += monthly_complaints * duration_months
        
        return {
            'total_estimated': round(total_estimated_complaints),
            'monthly_average': round(total_estimated_complaints / duration_months),
            'peak_complaint_period': 'First 2 months of construction'
        }