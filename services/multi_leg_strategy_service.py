"""
Multi-Leg Strategy Service
Handles execution of complex multi-leg option strategies (Iron Condor, Straddle, etc.)
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, time as time_obj
import pytz

from database.strategy_db import get_strategy
from database.strategy_leg_db import (
    create_strategy_leg, get_strategy_legs, update_leg_entry, update_leg_exit,
    update_leg_ltp, StrategyLeg
)
from database.auth_db import get_api_key_for_tradingview
from services.order_queue_service import queue_order
from utils.logging import get_logger

logger = get_logger(__name__)
IST = pytz.timezone('Asia/Kolkata')


class MultiLegStrategyService:
    """Service for managing multi-leg option strategies"""
    
    def __init__(self):
        """Initialize the service"""
        pass
    
    def parse_strategy_json(self, strategy_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse and validate strategy JSON
        
        Args:
            strategy_json: Strategy configuration JSON
            
        Returns:
            Parsed and validated strategy data
        """
        try:
            # Validate required fields
            required_fields = ['strategy_name', 'legs']
            for field in required_fields:
                if field not in strategy_json:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate legs
            legs = strategy_json.get('legs', [])
            if not legs or len(legs) == 0:
                raise ValueError("Strategy must have at least one leg")
            
            # Validate each leg
            for i, leg in enumerate(legs):
                leg_required = ['symbol', 'exchange', 'transaction_type', 'quantity']
                for field in leg_required:
                    if field not in leg:
                        raise ValueError(f"Leg {i} missing required field: {field}")
            
            return {
                'name': strategy_json.get('strategy_name'),
                'portfolio_risk': strategy_json.get('portfolio_risk', {}),
                'order_mode': strategy_json.get('order_mode', 'LIVE'),
                'legs': legs,
                'exit_rules': strategy_json.get('exit_rules', {}),
                'meta': strategy_json.get('meta', {})
            }
            
        except Exception as e:
            logger.error(f"Error parsing strategy JSON: {str(e)}", exc_info=True)
            raise
    
    def create_strategy_from_json(self, strategy_json: Dict[str, Any], user_id: str, 
                                   webhook_id: str = None) -> Optional[int]:
        """
        Create a strategy from JSON configuration
        
        Args:
            strategy_json: Strategy configuration JSON
            user_id: User ID
            webhook_id: Optional webhook ID (generated if not provided)
            
        Returns:
            Strategy ID or None if creation failed
        """
        try:
            import uuid
            from database.strategy_db import create_strategy
            
            parsed = self.parse_strategy_json(strategy_json)
            
            # Generate webhook ID if not provided
            if not webhook_id:
                webhook_id = str(uuid.uuid4())
            
            # Create strategy record
            strategy = create_strategy(
                name=parsed['name'],
                webhook_id=webhook_id,
                user_id=user_id,
                is_intraday=True,  # Multi-leg strategies are typically intraday
                trading_mode='BOTH',  # Multi-leg can be both
                platform='multi_leg',
                start_time=None,  # Will be set from execution_times
                end_time=None,
                squareoff_time=parsed['exit_rules'].get('square_off_time')
            )
            
            if not strategy:
                logger.error("Failed to create strategy record")
                return None
            
            # Store full JSON config
            strategy.strategy_config = json.dumps(strategy_json)
            strategy.order_mode = parsed['order_mode']
            
            # Store portfolio risk
            portfolio_risk = parsed.get('portfolio_risk', {})
            if portfolio_risk:
                strategy.portfolio_max_loss = portfolio_risk.get('max_loss')
                strategy.portfolio_max_profit = portfolio_risk.get('max_profit')
                strategy.stop_on_drawdown = portfolio_risk.get('stop_on_drawdown', False)
            
            from database.strategy_db import db_session
            db_session.commit()
            
            # Create leg records
            legs = parsed.get('legs', [])
            for leg_index, leg_data in enumerate(legs):
                leg = create_strategy_leg(strategy.id, leg_index, leg_data)
                if not leg:
                    logger.error(f"Failed to create leg {leg_index} for strategy {strategy.id}")
                    # Continue with other legs
            
            logger.info(f"Created multi-leg strategy {strategy.id} with {len(legs)} legs")
            return strategy.id
            
        except Exception as e:
            logger.error(f"Error creating strategy from JSON: {str(e)}", exc_info=True)
            return None
    
    def check_entry_conditions(self, leg: StrategyLeg) -> tuple[bool, str]:
        """
        Check if entry conditions are met for a leg
        
        Args:
            leg: Strategy leg to check
            
        Returns:
            Tuple of (can_enter, reason)
        """
        try:
            leg_id = leg.id if hasattr(leg, 'id') else 'unknown'
            
            # Check time-based entry condition
            if leg.entry_time_after:
                try:
                    now = datetime.now(IST)
                    entry_time = datetime.strptime(str(leg.entry_time_after), '%H:%M').time()
                    current_time = now.time()
                    
                    if current_time < entry_time:
                        return False, f"Entry time not reached: {leg.entry_time_after}"
                except (ValueError, AttributeError, TypeError) as e:
                    logger.warning(f"Error parsing entry_time_after for leg {leg_id}: {str(e)}")
                    # Continue with other checks
            
            # Check LTP-based entry condition
            if leg.entry_ltp_above is not None and leg.current_ltp is not None:
                try:
                    entry_ltp = float(leg.entry_ltp_above)
                    current_ltp = float(leg.current_ltp)
                    if current_ltp <= entry_ltp:
                        return False, f"LTP {current_ltp} not above {entry_ltp}"
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error comparing LTP for leg {leg_id}: {str(e)}")
                    # Continue with other checks
            
            return True, "Entry conditions met"
            
        except Exception as e:
            leg_id = leg.id if hasattr(leg, 'id') else 'unknown'
            logger.error(f"Error checking entry conditions for leg {leg_id}: {str(e)}", exc_info=True)
            return False, f"Error checking conditions: {str(e)}"
    
    def execute_strategy_legs(self, strategy_id: int) -> Dict[str, Any]:
        """
        Execute all legs of a multi-leg strategy
        
        Args:
            strategy_id: Strategy ID
            
        Returns:
            Execution results
        """
        try:
            strategy = get_strategy(strategy_id)
            if not strategy:
                return {'success': False, 'message': 'Strategy not found'}
            
            # Get API key
            api_key = get_api_key_for_tradingview(strategy.user_id)
            if not api_key:
                return {'success': False, 'message': 'No API key found'}
            
            # Get all legs
            legs = get_strategy_legs(strategy_id)
            if not legs:
                return {'success': False, 'message': 'No legs found for strategy'}
            
            executed_legs = []
            failed_legs = []
            
            # Execute each leg
            for leg in legs:
                # Check entry conditions
                can_enter, reason = self.check_entry_conditions(leg)
                if not can_enter:
                    logger.info(f"Leg {leg.id} entry conditions not met: {reason}")
                    failed_legs.append({'leg_id': leg.id, 'reason': reason})
                    continue
                
                # Build order payload
                order_payload = self._build_leg_order_payload(leg, strategy)
                
                # Queue the order
                queue_order('placeorder', order_payload)
                executed_legs.append(leg.id)
                logger.info(f"Queued order for leg {leg.id}: {leg.symbol} {leg.transaction_type} {leg.quantity}")
            
            return {
                'success': True,
                'executed_legs': executed_legs,
                'failed_legs': failed_legs,
                'total_legs': len(legs)
            }
            
        except Exception as e:
            logger.error(f"Error executing strategy legs: {str(e)}", exc_info=True)
            return {'success': False, 'message': str(e)}
    
    def _build_leg_order_payload(self, leg: StrategyLeg, strategy) -> Dict[str, Any]:
        """
        Build order payload for a leg
        
        Args:
            leg: Strategy leg
            strategy: Strategy object
            
        Returns:
            Order payload dictionary
        """
        try:
            # Validate that symbol is not a template variable
            if leg.symbol and (leg.symbol.startswith("{{") and leg.symbol.endswith("}}")):
                raise ValueError(
                    f"Invalid symbol in leg {leg.id if hasattr(leg, 'id') else 'unknown'}: "
                    f"'{leg.symbol}' appears to be a template variable that was not replaced. "
                    f"Please ensure the symbol is properly set in the strategy configuration."
                )
            
            # Build symbol name for options
            symbol = leg.symbol
            if leg.option_type and leg.strike is not None and leg.expiry:
                try:
                    # Format: NIFTY08JAN23500CE or NIFTY08JAN23500PE
                    # This is broker-specific, may need adjustment
                    expiry_parts = str(leg.expiry).split('-')
                    if len(expiry_parts) == 3:
                        year = expiry_parts[0][2:]  # Last 2 digits
                        month = expiry_parts[1]
                        day = expiry_parts[2]
                        # Convert month to abbreviation (01 -> JAN, etc.)
                        month_map = {
                            '01': 'JAN', '02': 'FEB', '03': 'MAR', '04': 'APR',
                            '05': 'MAY', '06': 'JUN', '07': 'JUL', '08': 'AUG',
                            '09': 'SEP', '10': 'OCT', '11': 'NOV', '12': 'DEC'
                        }
                        month_abbr = month_map.get(month, month)
                        strike_int = int(float(leg.strike)) if leg.strike else 0
                        symbol = f"{leg.symbol}{day}{month_abbr}{year}{strike_int}{leg.option_type}"
                except (ValueError, AttributeError, TypeError) as e:
                    logger.warning(f"Error building option symbol for leg {leg.id}: {str(e)}, using base symbol")
                    symbol = leg.symbol
            
            payload = {
                'apikey': get_api_key_for_tradingview(strategy.user_id),
                'strategy': strategy.name,
                'symbol': symbol,
                'action': leg.transaction_type,
                'exchange': leg.exchange,
                'price_type': leg.price_type or 'MARKET',
                'product': leg.product,
                'quantity': leg.quantity
            }
            
            if leg.price_type == 'LIMIT' and leg.limit_price is not None:
                try:
                    payload['price'] = float(leg.limit_price)
                except (ValueError, TypeError):
                    logger.warning(f"Invalid limit_price for leg {leg.id}, using MARKET order")
                    payload['price_type'] = 'MARKET'
            
            return payload
        except Exception as e:
            logger.error(f"Error building order payload for leg {leg.id if hasattr(leg, 'id') else 'unknown'}: {str(e)}", exc_info=True)
            raise
    
    def execute_single_leg(self, leg_id: int) -> Dict[str, Any]:
        """
        Execute a single leg
        
        Args:
            leg_id: Leg ID
            
        Returns:
            Execution result
        """
        try:
            from database.strategy_leg_db import get_strategy_leg_by_id, db_session
            leg = get_strategy_leg_by_id(leg_id)
            if not leg:
                return {'success': False, 'message': 'Leg not found'}
            
            if leg.status != 'PENDING':
                return {'success': False, 'message': f'Leg is already {leg.status}'}
            
            strategy = get_strategy(leg.strategy_id)
            if not strategy:
                return {'success': False, 'message': 'Strategy not found'}
            
            # Check entry conditions
            can_enter, reason = self.check_entry_conditions(leg)
            if not can_enter:
                return {'success': False, 'message': reason}
            
            # Build order payload
            order_payload = self._build_leg_order_payload(leg, strategy)
            
            # Queue the order
            queue_order('placeorder', order_payload)
            
            logger.info(f"Queued order for leg {leg_id}: {leg.symbol} {leg.transaction_type} {leg.quantity}")
            
            return {
                'success': True,
                'leg_id': leg_id,
                'message': f'Order queued for leg {leg_id}'
            }
            
        except Exception as e:
            logger.error(f"Error executing leg {leg_id}: {str(e)}", exc_info=True)
            return {'success': False, 'message': str(e)}
    
    def squareoff_single_leg(self, leg_id: int) -> Dict[str, Any]:
        """
        Square off a single leg
        
        Args:
            leg_id: Leg ID
            
        Returns:
            Square off result
        """
        try:
            from database.strategy_leg_db import get_strategy_leg_by_id, db_session
            leg = get_strategy_leg_by_id(leg_id)
            if not leg:
                return {'success': False, 'message': 'Leg not found'}
            
            if leg.status != 'ENTERED':
                return {'success': False, 'message': f'Leg is not entered (status: {leg.status})'}
            
            if not leg.entry_order_id:
                return {'success': False, 'message': 'No entry order found for leg'}
            
            strategy = get_strategy(leg.strategy_id)
            if not strategy:
                return {'success': False, 'message': 'Strategy not found'}
            
            # Build exit order payload (opposite transaction type)
            exit_transaction = 'BUY' if leg.transaction_type == 'SELL' else 'SELL'
            
            # Build symbol name for options
            symbol = leg.symbol
            if leg.option_type and leg.strike and leg.expiry:
                expiry_parts = leg.expiry.split('-')
                if len(expiry_parts) == 3:
                    year = expiry_parts[0][2:]
                    month = expiry_parts[1]
                    day = expiry_parts[2]
                    month_map = {
                        '01': 'JAN', '02': 'FEB', '03': 'MAR', '04': 'APR',
                        '05': 'MAY', '06': 'JUN', '07': 'JUL', '08': 'AUG',
                        '09': 'SEP', '10': 'OCT', '11': 'NOV', '12': 'DEC'
                    }
                    month_abbr = month_map.get(month, month)
                    symbol = f"{leg.symbol}{day}{month_abbr}{year}{int(leg.strike)}{leg.option_type}"
            
            exit_payload = {
                'apikey': get_api_key_for_tradingview(strategy.user_id),
                'strategy': strategy.name,
                'symbol': symbol,
                'action': exit_transaction,
                'exchange': leg.exchange,
                'price_type': 'MARKET',
                'product': leg.product,
                'quantity': leg.entry_filled_qty or leg.quantity
            }
            
            # Queue the exit order
            queue_order('placeorder', exit_payload)
            
            logger.info(f"Queued square off order for leg {leg_id}: {symbol} {exit_transaction} {exit_payload['quantity']}")
            
            return {
                'success': True,
                'leg_id': leg_id,
                'message': f'Square off order queued for leg {leg_id}'
            }
            
        except Exception as e:
            logger.error(f"Error squaring off leg {leg_id}: {str(e)}", exc_info=True)
            return {'success': False, 'message': str(e)}

