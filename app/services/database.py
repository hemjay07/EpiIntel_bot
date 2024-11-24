# app/services/database.py
from typing import Dict, List, Optional
from supabase import create_client, Client
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DiseaseDataService:
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )

    def get_latest_report(self, disease_type: str) -> Dict:
        """Get the latest report ID for a disease"""
        try:
            response = self.supabase.table('outbreak_reports')\
                .select('*')\
                .eq('disease_type', disease_type)\
                .order('reporting_week', desc=True)\
                .limit(1)\
                .execute()
                
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching latest report: {str(e)}")
            return None

    def get_disease_summary(self, disease_type: str) -> Dict:
        """Get current summary for a specific disease"""
        try:
            # First get the latest report
            latest_report = self.get_latest_report(disease_type)
            if not latest_report:
                return None
                
            # Then get the case data for this report
            response = self.supabase.table('disease_cases')\
                .select('*')\
                .eq('report_id', latest_report['id'])\
                .limit(1)\
                .execute()
                
            if not response.data:
                return None
                
            data = response.data[0]
            weekly_stats = data['weekly_national_stats']
            cumulative_stats = data['cumulative_national_stats']
            
            # Format response based on disease type
            if disease_type == 'mpox':
                return {
                    'weekly': {
                        'confirmed_cases': weekly_stats.get('confirmed_cases', 0),
                        'suspected_cases': weekly_stats.get('suspected_cases', 0),
                        'deaths': weekly_stats.get('deaths', 0),
                        'coinfection_cases': weekly_stats.get('coinfection_cases', 0)
                    },
                    'cumulative': {
                        'confirmed_cases': cumulative_stats.get('confirmed_cases', 0),
                        'suspected_cases': cumulative_stats.get('suspected_cases', 0),
                        'deaths': cumulative_stats.get('deaths', 0),
                        'male_cases': cumulative_stats.get('male_cases', 0),
                        'female_cases': cumulative_stats.get('female_cases', 0),
                        'states_affected': cumulative_stats.get('states_affected', '0')
                    },
                    'reporting_week': latest_report['reporting_week'],
                    'reporting_year': latest_report['reporting_year']
                }
            else:  # cholera
                return {
                    'weekly': {
                        'suspected_cases': weekly_stats.get('suspected_cases', 0),
                        'deaths': weekly_stats.get('deaths', 0),
                        'cfr': weekly_stats.get('case_fatality_ratio', 0)
                    },
                    'cumulative': {
                        'suspected_cases': cumulative_stats.get('suspected_cases', 0),
                        'deaths': cumulative_stats.get('deaths', 0),
                        'cfr': cumulative_stats.get('case_fatality_ratio', 0)
                    },
                    'reporting_week': latest_report['reporting_week'],
                    'reporting_year': latest_report['reporting_year']
                }
            
        except Exception as e:
            logger.error(f"Error fetching disease summary: {str(e)}")
            return None

    def get_state_data(self, disease_type: str, state: str) -> Dict:
        """Get disease data for a specific state"""
        try:
            # First get the latest report
            latest_report = self.get_latest_report(disease_type)
            if not latest_report:
                return None
                
            # Then get the case data for this report
            response = self.supabase.table('disease_cases')\
                .select('*')\
                .eq('report_id', latest_report['id'])\
                .limit(1)\
                .execute()
                
            if not response.data:
                return None
                
            data = response.data[0]
            
            # Get state statistics
            weekly_state_stats = data['weekly_state_stats'] if data.get('weekly_state_stats') else {}
            cumulative_state_stats = data['cumulative_state_stats'] if data.get('cumulative_state_stats') else {}
            
            # Get state ranking
            ranking_response = self.supabase.table('geographic_rankings')\
                .select('*')\
                .eq('report_id', latest_report['id'])\
                .limit(1)\
                .execute()
                
            ranking_info = None
            if ranking_response.data:
                rankings = ranking_response.data[0]['top_states']['rankings']
                state_ranking = next((r for r in rankings if r['state'] == state), None)
                if state_ranking:
                    ranking_info = {
                        'rank': state_ranking['rank'],
                        'percentage': state_ranking['percentage']
                    }
            
            return {
                'weekly_state_stats': weekly_state_stats,
                'cumulative_state_stats': cumulative_state_stats,
                'reporting_week': latest_report['reporting_week'],
                'reporting_year': latest_report['reporting_year'],
                'ranking': ranking_info
            }
                
        except Exception as e:
            print(f"Error fetching state data: {str(e)}")
            return None

    def get_state_rankings(self, disease_type: str, limit: int = 5) -> List[Dict]:
        """Get top affected states"""
        try:
            latest_report = self.get_latest_report(disease_type)
            if not latest_report:
                return None
                
            response = self.supabase.table('geographic_rankings')\
                .select('*')\
                .eq('report_id', latest_report['id'])\
                .limit(1)\
                .execute()
                
            if not response.data:
                return None
                
            rankings = response.data[0]['top_states']['rankings']
            return rankings[:limit]
            
        except Exception as e:
            logger.error(f"Error fetching state rankings: {str(e)}")
            return None