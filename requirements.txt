# Add this to your app's views.py (e.g., trading/views.py)
import ccxt
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def index(request):
    return render(request, 'index.html')

def new_coin_guide(request):
    return render(request, 'new_coin_checklist.html')


def new_coin_patterns(request):
    return render(request, 'new_coin_patterns.html')


def new_coin_analysis(request):
    return render(request, 'new_coin_analysis.html')

def new_coin_strategy(request):
    return render(request, 'new_coin_strategy.html')

patterns = [
    {
        "id": 1,
        "name": "Pump → Dump → Accumulate → Pump (Classic Retail Trap)",
        "indicators": {"initial_pump": ">20%", "dump_depth": ">30%", "volume_spike": True, "volume_collapse": True, "whale_accum": True, "hype_high": True, "private_yes": True, "fdv_high": True},
        "advice": "Wait for range + volume retest; enter breakout with 1:3 RR",
        "next_move": "20-50% pump after accumulation (90% likelihood if whale inflows confirm)"
    },
    {
        "id": 2,
        "name": "Instant Dump → Range → Slow Recovery (VC Dump / Early Investor Exit)",
        "indicators": {"initial_dump": ">20%", "range_flat": True, "unlock_cliff": ">10%", "no_bounce": True, "private_yes": True, "holders_concentrated": True},
        "advice": "Buy range lows after unlock cliff; trail stops on recovery",
        "next_move": "10-30% recovery over 48h (85% if vesting clears)"
    },
    {
        "id": 3,
        "name": "Slow Bleed Downwards (Low Demand, High FDV)",
        "indicators": {"daily_decline": "1-5%", "no_spikes": True, "high_fdv": ">500M", "low_volume": True, "hype_low": True, "utility_weak": True},
        "advice": "Avoid; wait 1-2 weeks for capitulation bottom",
        "next_move": "Continued 5-15% bleed (95% if no narrative shift)"
    },
    {
        "id": 4,
        "name": "Pump → Hold High → Expand (Institutional Support)",
        "indicators": {"tight_consol": "5-10%", "green_closes": ">80%", "shallow_pull": "<5%", "inst_inflow": True, "smart_entering": True, "order_thick": True, "backers_strong": True},
        "advice": "Buy dips to EMA20; scale out at fib extensions",
        "next_move": "50%+ expansion (92% with inst inflows)"
    },
    {
        "id": 5,
        "name": "Fake Pump → Sharp Dump → Dead Range (Dead-on-Arrival)",
        "indicators": {"bot_spike": ">50%", "sharp_dump": ">60%", "low_org_vol": True, "dev_dump": ">20%", "hype_low": True, "team_anon": True, "audit_none": True},
        "advice": "Avoid entirely; short if perp available",
        "next_move": "Dead flat or further 30% dump (98% rug risk)"
    },
    {
        "id": 6,
        "name": "Sideways First → Breakout Later (Stealth Accumulation)",
        "indicators": {"flat_range": True, "low_vol": "<10%", "spor_vol_spikes": True, "multi_wallet_buy": True, "initial_sideways": True, "float_low": "<25%", "whale_inflows": True},
        "advice": "Enter post-break + retest; use volume profile for targets",
        "next_move": "100%+ breakout (90% on vol confirmation)"
    },
    {
        "id": 7,
        "name": "Pump → Fake Dump → V-Shaped Recovery (Liquidity Trap)",
        "indicators": {"sweep_dump": "15-25%", "v_reversal": True, "high_vol_reclaim": True, "smart_entering": True, "liquidity_thin": True},
        "advice": "Enter V-bottom; target prior high",
        "next_move": "V-recovery to new highs (88% if reclaim holds)"
    },
    {
        "id": 8,
        "name": "Announcement Arb Pump → Quick Fade (Bot Frenzy)",
        "indicators": {"pre_list_spike": "30-100%", "post_fade": "20-40%", "arb_vol": True, "thin_bids": True, "order_thin": True, "bot_tx_high": True},
        "advice": "Fade peak with tight stop; avoid if no fundamentals",
        "next_move": "Quick 20-40% fade (95% on thin books)"
    },
    {
        "id": 9,
        "name": "Futures-Led Cascade (Perp Dominance)",
        "indicators": {"perp_vol_dom": ">80%", "liq_cascade": True, "neg_funding": True, "order_thin": True, "oi_high": True},
        "advice": "Short perps on high OI; hedge spot long",
        "next_move": "Cascade dump 10-30% (92% on neg funding)"
    },
    {
        "id": 10,
        "name": "Exploit/Backlash Dump → Rebound (Narrative Fix)",
        "indicators": {"news_crash": ">50%", "sent_drop": "<50", "team_fix": True, "audit_partial": True},
        "advice": "Buy post-fix dip; cap at 1% position",
        "next_move": "Partial rebound 15-40% (85% if fix announced)"
    },
    {
        "id": 11,
        "name": "Delisting Shadow (Temporary Pump → Bleed)",
        "indicators": {"low_vol_week": "<50%", "contract_change": True, "lower_highs": True, "compliance_issue": True},
        "advice": "Exit early; monitor for re-list signals",
        "next_move": "Slow bleed 10-20% (96% pre-delist)"
    },
    {
        "id": 12,
        "name": "Narrative Rotation Surge (Chain Hop)",
        "indicators": {"theme_shift": True, "whale_transfers": True, "x_mentions_spike": "5x", "hype_high": True, "competitor_overlap": False},
        "advice": "Enter on rotation confirm; exit on next signal",
        "next_move": "Surge pump 30-80% (91% on hot narrative)"
    }
]

def match_pattern_and_predict(inputs):
    scores = {p["id"]: 0 for p in patterns}
    overall_confidence = 0  # Build to >90% threshold
    
    # Comprehensive scoring integrating all factors
    # Fundamentals (40% weight)
    fdv = inputs.get('fdv', 0)
    if fdv > 500000000:
        scores[3] += 3  # High FDV boosts bleed
        scores[2] += 1
    vesting_cliff = inputs.get('vesting_cliff', 0)
    if vesting_cliff > 10:
        scores[2] += 3
    team_score = inputs.get('team_score', 5)  # 1-10
    if team_score >= 8:
        scores[4] += 2
        scores[10] += 1
    else:
        scores[5] += 2
    utility_score = inputs.get('utility_score', 5)  # 1-10
    if utility_score < 4:
        scores[3] += 2
        scores[5] += 2
    audit_status = inputs.get('audit_status', 'none')
    if audit_status == 'full':
        overall_confidence += 10
    elif audit_status == 'partial':
        scores[10] += 2
    else:
        scores[5] += 3
        overall_confidence -= 5  # Penalize for risk
    
    # On-Chain (30% weight)
    holders_concentrated = inputs.get('holders_concentrated', False)
    if holders_concentrated:
        scores[2] += 2
        scores[5] += 2
    liquidity_depth = inputs.get('liquidity_depth', 500000)  # USD
    if liquidity_depth < 100000:
        scores[8] += 2
        scores[9] += 2
        overall_confidence -= 10
    whale_inflows = inputs.get('whale_inflows', False)
    if whale_inflows:
        scores[1] += 2
        scores[4] += 2
        scores[6] += 2
        overall_confidence += 15
    dev_dump = inputs.get('dev_dump', 0)
    if dev_dump > 20:
        scores[5] += 3
    bot_tx_high = inputs.get('bot_tx_high', False)
    if bot_tx_high:
        scores[8] += 3
    
    # Technical (20% weight)
    initial_action = inputs.get('initialAction', '')
    if initial_action == 'pump':
        scores[1] += 2
        scores[5] += 1
        scores[7] += 1
        scores[8] += 1
    elif initial_action == 'dump':
        scores[2] += 2
        scores[7] += 1
        scores[10] += 1
    elif initial_action == 'sideways':
        scores[6] += 3
        scores[11] += 1
    elif initial_action == 'smallpump':
        scores[4] += 2
    rsi = inputs.get('rsi', 50)
    if rsi > 80:
        scores[8] += 2
    elif rsi < 30:
        scores[2] += 1
        scores[10] += 1
    neg_funding = inputs.get('neg_funding', False)
    if neg_funding:
        scores[9] += 3
    
    # Market/Sentiment (10% weight)
    hype = inputs.get('hype', 'medium')
    if hype == 'high':
        scores[1] += 1
        scores[12] += 2
        overall_confidence += 5
    elif hype == 'low':
        scores[3] += 2
        scores[5] += 1
    social_mentions = inputs.get('social_mentions', 1)  # Multiplier
    if social_mentions > 5:
        scores[12] += 2
    macro_bullish = inputs.get('macro_bullish', False)
    if macro_bullish:
        scores[4] += 1
        scores[12] += 1
        overall_confidence += 10
    competitor_overlap = inputs.get('competitor_overlap', True)
    if not competitor_overlap:
        scores[12] += 1
    
    # Normalize confidence (scale to 100; threshold for >90%)
    overall_confidence = min(100, max(0, overall_confidence + 50))  # Base 50, adjust by factors
    
    # Find highest score
    max_score = max(scores.values())
    if max_score == 0:
        return "No clear pattern matched. Monitor fundamentals and re-run with more data.", "", 0
    
    matched_id = max(scores, key=scores.get)
    matched_pattern = next(p for p in patterns if p["id"] == matched_id)
    next_move = matched_pattern["next_move"] if overall_confidence > 90 else f"{matched_pattern['next_move']} (confidence: {overall_confidence}%)"
    
    return matched_pattern["name"], matched_pattern["advice"], next_move

def new_coin_analyzer(request):
    if request.method == 'POST':
        # Parse expanded form data
        inputs = {
            'fdv': float(request.POST.get('fdv', 0) or 0),
            'vesting_cliff': float(request.POST.get('vesting_cliff', 0) or 0),
            'team_score': int(request.POST.get('team_score', 5) or 5),
            'utility_score': int(request.POST.get('utility_score', 5) or 5),
            'audit_status': request.POST.get('audit_status', 'none'),
            'holders_concentrated': request.POST.get('holders_concentrated', 'no') == 'yes',
            'liquidity_depth': float(request.POST.get('liquidity_depth', 500000) or 500000),
            'whale_inflows': request.POST.get('whale_inflows', 'no') == 'yes',
            'dev_dump': float(request.POST.get('dev_dump', 0) or 0),
            'bot_tx_high': request.POST.get('bot_tx_high', 'no') == 'yes',
            'initialAction': request.POST.get('initialAction', ''),
            'rsi': float(request.POST.get('rsi', 50) or 50),
            'neg_funding': request.POST.get('neg_funding', 'no') == 'yes',
            'hype': request.POST.get('hype', 'medium'),
            'social_mentions': float(request.POST.get('social_mentions', 1) or 1),
            'macro_bullish': request.POST.get('macro_bullish', 'no') == 'yes',
            'competitor_overlap': request.POST.get('competitor_overlap', 'yes') == 'yes',
        }
        
        pattern_name, advice, next_move = match_pattern_and_predict(inputs)
        
        context = {
            'show_result': True,
            'pattern': pattern_name,
            'advice': advice,
            'next_move': next_move,
            'inputs': inputs,  # Pass back to repopulate
        }
        return render(request, 'new_coin_analyzer.html', context)
    
    return render(request, 'new_coin_analyzer.html', {'show_result': False})

def compute_correlation_analysis(coin_symbol, style):
    """
    Separate function to handle all correlation analysis computations.
    Returns a dict with results or raises exceptions for error handling.
    """
    if coin_symbol == 'BTC':
        raise ValueError('Cannot analyze BTC vs itself. Choose another coin.')
    
    pair = f"{coin_symbol}/USDT"
    
    tf_map = {
        'scalper': ('1h', 60),
        'day': ('4h', 60),
        'swing': ('1d', 60),
        'positional': ('1w', 60),
    }
    timeframe, window = tf_map.get(style, ('4h', 60))
    
    try:
        exchange = ccxt.binance()
        limit = window * 2
        
        ohlcv_btc = exchange.fetch_ohlcv('BTC/USDT', timeframe=timeframe, limit=limit)
        ohlcv_coin = exchange.fetch_ohlcv(pair, timeframe=timeframe, limit=limit)
        
        if len(ohlcv_btc) < window or len(ohlcv_coin) < window:
            raise ValueError(f'Insufficient historical data for {coin_symbol}/USDT on {timeframe} timeframe.')
        
        df_btc = pd.DataFrame(ohlcv_btc, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df_btc['timestamp'] = pd.to_datetime(df_btc['timestamp'], unit='ms')
        df_btc.set_index('timestamp', inplace=True)
        
        df_coin = pd.DataFrame(ohlcv_coin, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df_coin['timestamp'] = pd.to_datetime(df_coin['timestamp'], unit='ms')
        df_coin.set_index('timestamp', inplace=True)
        
        # Improved alignment: Use DataFrame constructor for explicit columns
        df_aligned = pd.DataFrame({
            'BTC_close': df_btc['close'],
            f'{coin_symbol}_close': df_coin['close']
        })
        
        # Check alignment
        if df_aligned.isnull().all().any():  # If entire column NaN
            raise ValueError('Data synchronization failed - mismatched timestamps.')
        
        # Calculate returns
        df_aligned['BTC_returns'] = df_aligned['BTC_close'].pct_change()
        df_aligned[f'{coin_symbol}_returns'] = df_aligned[f'{coin_symbol}_close'].pct_change()
        
        # Drop NaNs from returns
        df_returns = df_aligned[['BTC_returns', f'{coin_symbol}_returns']].dropna()
        
        if len(df_returns) < window:
            raise ValueError(f'Insufficient overlapping data for rolling correlation (need {window} periods, got {len(df_returns)}).')
        
        # Calculate rolling correlation
        rolling_corr = df_returns['BTC_returns'].rolling(window=window).corr(df_returns[f'{coin_symbol}_returns'])
        rolling_corr = rolling_corr.dropna()
        
        if len(rolling_corr) == 0:
            raise ValueError('Unable to compute rolling correlation - data too sparse.')
        
        current_corr = rolling_corr.iloc[-1]
        
        # Gauge plot
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=current_corr,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"Current {timeframe.upper()} Correlation: {current_corr:.3f}", 'font': {'size': 24}},
            gauge={
                'axis': {'range': [-1, 1], 'tickwidth': 1, 'tickcolor': "black"},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [-1, -0.5], 'color': "red"},
                    {'range': [-0.5, 0], 'color': "orange"},
                    {'range': [0, 0.5], 'color': "yellow"},
                    {'range': [0.5, 1], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': abs(current_corr) if abs(current_corr) > 0.8 else 0.8
                }
            }
        ))
        gauge_plot = fig_gauge.to_html(full_html=False, include_plotlyjs='cdn')
        
        # Historical correlation chart
        fig_corr = go.Figure()
        fig_corr.add_trace(go.Scatter(
            x=rolling_corr.index,
            y=rolling_corr.values,
            mode='lines',
            name='Rolling Correlation',
            line=dict(color='blue', width=2)
        ))
        fig_corr.add_hline(y=0.8, line_dash="dash", line_color="green", annotation_text="Strong Positive")
        fig_corr.add_hline(y=-0.8, line_dash="dash", line_color="red", annotation_text="Strong Negative")
        fig_corr.add_hline(y=0, line_dash="dot", line_color="gray")
        fig_corr.update_layout(
            title=f'Rolling Correlation Trend ({timeframe.upper()}, Window: {window} periods)',
            xaxis_title='Time',
            yaxis_title='Correlation Coefficient',
            yaxis_range=[-1, 1]
        )
        corr_plot = fig_corr.to_html(full_html=False, include_plotlyjs='cdn')
        
        # Normalized price paths (using df_aligned for consistency)
        df_aligned['BTC_cum_returns'] = (1 + df_aligned['BTC_returns']).cumprod().fillna(1)
        df_aligned[f'{coin_symbol}_cum_returns'] = (1 + df_aligned[f'{coin_symbol}_returns']).cumprod().fillna(1)
        
        fig_price = make_subplots(specs=[[{"secondary_y": True}]])
        fig_price.add_trace(
            go.Scatter(x=df_aligned.index, y=df_aligned['BTC_cum_returns'], name='BTC (Normalized)', line=dict(color='blue')),
            secondary_y=False
        )
        fig_price.add_trace(
            go.Scatter(x=df_aligned.index, y=df_aligned[f'{coin_symbol}_cum_returns'], name=f'{coin_symbol} (Normalized)', line=dict(color='orange')),
            secondary_y=True
        )
        fig_price.update_layout(
            title=f'Normalized Price Paths ({timeframe.upper()})',
            xaxis_title='Time',
            yaxis_title='Normalized Cumulative Returns'
        )
        fig_price.update_yaxes(title_text="BTC", secondary_y=False)
        fig_price.update_yaxes(title_text=coin_symbol, secondary_y=True)
        price_plot = fig_price.to_html(full_html=False, include_plotlyjs='cdn')
        
        return {
            'current_corr': round(float(current_corr), 3),
            'timeframe': timeframe,
            'coin_symbol': coin_symbol,
            'gauge_plot': gauge_plot,
            'corr_plot': corr_plot,
            'price_plot': price_plot,
            'style': style,
        }
    
    except ccxt.NetworkError:
        raise Exception('Network issue fetching data from exchange. Try again later.')
    except ccxt.BadSymbol:
        raise ValueError(f'Invalid trading pair: {pair}. Check the coin symbol.')
    except KeyError as ke:
        raise Exception(f'Data processing error (missing column: {ke}). Ensure valid inputs.')
    except Exception as e:
        raise Exception(f'Unexpected error: {str(e)}')

@csrf_exempt
def correlation_visualizer(request):
    if request.method == 'POST':
        style = request.POST.get('style', 'day')
        coin_symbol = request.POST.get('coin_symbol', 'ETH').upper()
        
        try:
            analysis_results = compute_correlation_analysis(coin_symbol, style)
            style_options = [
                ('scalper', 'Scalper'),
                ('day', 'Day Trader'),
                ('swing', 'Swing Trader'),
                ('positional', 'Positional Trader'),
            ]
            context = {
                'style_options': style_options,
                **analysis_results
            }
            return render(request, 'correlation_visualizer.html', context)
        
        except ValueError as ve:
            return JsonResponse({'error': str(ve)}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    # GET request
    style_options = [
        ('scalper', 'Scalper'),
        ('day', 'Day Trader'),
        ('swing', 'Swing Trader'),
        ('positional', 'Positional Trader'),
    ]
    context = {'style_options': style_options}
    return render(request, 'correlation_visualizer.html', context)