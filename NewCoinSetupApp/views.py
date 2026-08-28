import ccxt
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import random
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, Avg, Q

from .models import TradeEntry, UserProfile, PATTERN_TAG_CHOICES, PSYCHOLOGY_CHOICES
from .forms import CustomUserCreationForm, EmailOrUsernameAuthenticationForm

# ==========================================================
# PUBLIC PAGES & EXISTING INTELLIGENCE ENGINES
# ==========================================================

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
    overall_confidence = 0
    
    fdv = inputs.get('fdv', 0)
    if fdv > 500000000:
        scores[3] += 3
        scores[2] += 1
    vesting_cliff = inputs.get('vesting_cliff', 0)
    if vesting_cliff > 10:
        scores[2] += 3
    team_score = inputs.get('team_score', 5)
    if team_score >= 8:
        scores[4] += 2
        scores[10] += 1
    else:
        scores[5] += 2
    utility_score = inputs.get('utility_score', 5)
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
        overall_confidence -= 5
    
    holders_concentrated = inputs.get('holders_concentrated', False)
    if holders_concentrated:
        scores[2] += 2
        scores[5] += 2
    liquidity_depth = inputs.get('liquidity_depth', 500000)
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
    
    hype = inputs.get('hype', 'medium')
    if hype == 'high':
        scores[1] += 1
        scores[12] += 2
        overall_confidence += 5
    elif hype == 'low':
        scores[3] += 2
        scores[5] += 1
    social_mentions = inputs.get('social_mentions', 1)
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
    
    overall_confidence = min(100, max(0, overall_confidence + 50))
    max_score = max(scores.values())
    if max_score == 0:
        return "No clear pattern matched. Monitor fundamentals and re-run with more data.", "", 0
    
    matched_id = max(scores, key=scores.get)
    matched_pattern = next(p for p in patterns if p["id"] == matched_id)
    next_move = matched_pattern["next_move"] if overall_confidence > 90 else f"{matched_pattern['next_move']} (confidence: {overall_confidence}%)"
    
    return matched_pattern["name"], matched_pattern["advice"], next_move

def new_coin_analyzer(request):
    if request.method == 'POST':
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
            'inputs': inputs,
        }
        return render(request, 'new_coin_analyzer.html', context)
    
    return render(request, 'new_coin_analyzer.html', {'show_result': False})

def compute_correlation_analysis(coin_symbol, style):
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
        
        df_aligned = pd.DataFrame({
            'BTC_close': df_btc['close'],
            f'{coin_symbol}_close': df_coin['close']
        })
        
        if df_aligned.isnull().all().any():
            raise ValueError('Data synchronization failed - mismatched timestamps.')
        
        df_aligned['BTC_returns'] = df_aligned['BTC_close'].pct_change()
        df_aligned[f'{coin_symbol}_returns'] = df_aligned[f'{coin_symbol}_close'].pct_change()
        
        df_returns = df_aligned[['BTC_returns', f'{coin_symbol}_returns']].dropna()
        
        if len(df_returns) < window:
            raise ValueError(f'Insufficient overlapping data for rolling correlation (need {window} periods, got {len(df_returns)}).')
        
        rolling_corr = df_returns['BTC_returns'].rolling(window=window).corr(df_returns[f'{coin_symbol}_returns'])
        rolling_corr = rolling_corr.dropna()
        
        if len(rolling_corr) == 0:
            raise ValueError('Unable to compute rolling correlation - data too sparse.')
        
        current_corr = rolling_corr.iloc[-1]
        
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=current_corr,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"Current {timeframe.upper()} Correlation: {current_corr:.3f}", 'font': {'size': 20, 'family': 'Inter, sans-serif'}},
            gauge={
                'axis': {'range': [-1, 1], 'tickwidth': 1, 'tickcolor': "#64748b"},
                'bar': {'color': "#2563eb"},
                'steps': [
                    {'range': [-1, -0.5], 'color': "#fee2e2"},
                    {'range': [-0.5, 0], 'color': "#fef3c7"},
                    {'range': [0, 0.5], 'color': "#e0e7ff"},
                    {'range': [0.5, 1], 'color': "#d1fae5"}
                ],
            }
        ))
        gauge_plot = fig_gauge.to_html(full_html=False, include_plotlyjs='cdn')
        
        fig_corr = go.Figure()
        fig_corr.add_trace(go.Scatter(
            x=rolling_corr.index,
            y=rolling_corr.values,
            mode='lines',
            name='Rolling Correlation',
            line=dict(color='#2563eb', width=2)
        ))
        fig_corr.add_hline(y=0.8, line_dash="dash", line_color="#10b981", annotation_text="Strong Positive")
        fig_corr.add_hline(y=-0.8, line_dash="dash", line_color="#ef4444", annotation_text="Strong Negative")
        fig_corr.add_hline(y=0, line_dash="dot", line_color="#94a3b8")
        fig_corr.update_layout(
            title=f'Rolling Correlation Trend ({timeframe.upper()})',
            template="plotly_white",
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font=dict(family="Inter, sans-serif", color="#0f172a")
        )
        corr_plot = fig_corr.to_html(full_html=False, include_plotlyjs='cdn')
        
        df_aligned['BTC_cum_returns'] = (1 + df_aligned['BTC_returns']).cumprod().fillna(1)
        df_aligned[f'{coin_symbol}_cum_returns'] = (1 + df_aligned[f'{coin_symbol}_returns']).cumprod().fillna(1)
        
        fig_price = make_subplots(specs=[[{"secondary_y": True}]])
        fig_price.add_trace(
            go.Scatter(x=df_aligned.index, y=df_aligned['BTC_cum_returns'], name='BTC (Normalized)', line=dict(color='#2563eb')),
            secondary_y=False
        )
        fig_price.add_trace(
            go.Scatter(x=df_aligned.index, y=df_aligned[f'{coin_symbol}_cum_returns'], name=f'{coin_symbol} (Normalized)', line=dict(color='#f59e0b')),
            secondary_y=True
        )
        fig_price.update_layout(
            title=f'Normalized Price Paths ({timeframe.upper()})',
            template="plotly_white",
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font=dict(family="Inter, sans-serif", color="#0f172a")
        )
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
    
    except Exception as e:
        raise Exception(f'Error fetching market data: {str(e)}')

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
        except Exception as e:
            return render(request, 'correlation_visualizer.html', {
                'style_options': [('scalper', 'Scalper'), ('day', 'Day Trader'), ('swing', 'Swing Trader'), ('positional', 'Positional Trader')],
                'error': str(e)
            })
    
    style_options = [
        ('scalper', 'Scalper'),
        ('day', 'Day Trader'),
        ('swing', 'Swing Trader'),
        ('positional', 'Positional Trader'),
    ]
    return render(request, 'correlation_visualizer.html', {'style_options': style_options})


# ==========================================================
# AUTHENTICATION & PROFILE SYSTEM
# ==========================================================

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('journal_dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to CoinIntel Journal, {user.username}!")
            return redirect('journal_dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('journal_dashboard')
    
    if request.method == 'POST':
        form = EmailOrUsernameAuthenticationForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username_or_email'].strip()
            password = form.cleaned_data['password']
            
            user_obj = User.objects.filter(Q(username__iexact=username_or_email) | Q(email__iexact=username_or_email)).first()
            if user_obj:
                user = authenticate(request, username=user_obj.username, password=password)
            else:
                user = None

            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('journal_dashboard')
            else:
                messages.error(request, "Invalid username/email or password.")
        else:
            messages.error(request, "Invalid login credentials.")
    else:
        form = EmailOrUsernameAuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('index')

@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        try:
            balance = float(request.POST.get('account_balance', profile.account_balance))
            risk_pct = float(request.POST.get('risk_per_trade_pct', profile.risk_per_trade_pct))
            tier = request.POST.get('trading_tier', profile.trading_tier)
            avatar = request.POST.get('avatar_symbol', profile.avatar_symbol)
            
            profile.account_balance = balance
            profile.risk_per_trade_pct = risk_pct
            profile.trading_tier = tier
            profile.avatar_symbol = avatar
            profile.save()
            messages.success(request, "Profile & account risk preferences updated successfully.")
        except ValueError:
            messages.error(request, "Invalid numeric input for balance or risk.")
        return redirect('profile')
    
    return render(request, 'registration/profile.html', {'profile': profile})


# ==========================================================
# MULTI-USER TRADE JOURNAL SYSTEM
# ==========================================================

@login_required
def journal_dashboard(request):
    user_trades = TradeEntry.objects.filter(user=request.user)
    
    total_trades = user_trades.count()
    closed_trades = user_trades.exclude(status='OPEN')
    winning_trades = user_trades.filter(status='CLOSED_WIN')
    losing_trades = user_trades.filter(status='CLOSED_LOSS')
    open_trades = user_trades.filter(status='OPEN')
    
    win_count = winning_trades.count()
    loss_count = losing_trades.count()
    total_closed = closed_trades.count()
    
    win_rate = round((win_count / total_closed * 100), 1) if total_closed > 0 else 0.0
    
    net_pnl = closed_trades.aggregate(Sum('pnl_usd'))['pnl_usd__sum'] or 0.0
    net_pnl = round(net_pnl, 2)
    
    gross_profit = winning_trades.aggregate(Sum('pnl_usd'))['pnl_usd__sum'] or 0.0
    gross_loss = abs(losing_trades.aggregate(Sum('pnl_usd'))['pnl_usd__sum'] or 0.0)
    profit_factor = round((gross_profit / gross_loss), 2) if gross_loss > 0 else (round(gross_profit, 2) if gross_profit > 0 else 0.0)
    
    avg_r = closed_trades.aggregate(Avg('r_multiple'))['r_multiple__avg'] or 0.0
    avg_r = round(avg_r, 2)
    
    recent_trades = user_trades[:6]
    
    context = {
        'total_trades': total_trades,
        'open_trades_count': open_trades.count(),
        'closed_trades_count': total_closed,
        'win_rate': win_rate,
        'net_pnl': net_pnl,
        'abs_net_pnl': round(abs(net_pnl), 2),
        'profit_factor': profit_factor,
        'avg_r': avg_r,
        'recent_trades': recent_trades,
        'open_trades': open_trades,
        'profile': getattr(request.user, 'profile', None),
    }
    return render(request, 'journal/dashboard.html', context)

@login_required
def trade_list(request):
    trades = TradeEntry.objects.filter(user=request.user)
    
    status_filter = request.GET.get('status', '')
    symbol_filter = request.GET.get('symbol', '').strip().upper()
    psychology_filter = request.GET.get('psychology', '')
    
    if status_filter:
        trades = trades.filter(status=status_filter)
    if symbol_filter:
        trades = trades.filter(symbol__icontains=symbol_filter)
    if psychology_filter:
        trades = trades.filter(psychology_state=psychology_filter)
    
    context = {
        'trades': trades,
        'status_filter': status_filter,
        'symbol_filter': symbol_filter,
        'psychology_filter': psychology_filter,
        'status_choices': TradeEntry._meta.get_field('status').choices,
        'psychology_choices': PSYCHOLOGY_CHOICES,
    }
    return render(request, 'journal/trade_list.html', context)

@login_required
def trade_create(request):
    if request.method == 'POST':
        try:
            symbol = request.POST.get('symbol', '').upper().strip()
            trade_type = request.POST.get('trade_type', 'LONG')
            status = request.POST.get('status', 'OPEN')
            
            entry_price = float(request.POST.get('entry_price', 0))
            exit_price_str = request.POST.get('exit_price', '').strip()
            exit_price = float(exit_price_str) if exit_price_str else None
            
            stop_loss_str = request.POST.get('stop_loss', '').strip()
            stop_loss = float(stop_loss_str) if stop_loss_str else None
            
            take_profit_str = request.POST.get('take_profit', '').strip()
            take_profit = float(take_profit_str) if take_profit_str else None
            
            position_size = float(request.POST.get('position_size_usd', 1000))
            leverage = int(request.POST.get('leverage', 1))
            
            pattern_tag = request.POST.get('pattern_tag', '')
            psychology_state = request.POST.get('psychology_state', 'DISCIPLINED')
            notes = request.POST.get('notes', '')
            chart_url = request.POST.get('chart_url', '').strip()
            
            trade = TradeEntry(
                user=request.user,
                symbol=symbol,
                trade_type=trade_type,
                status=status,
                entry_price=entry_price,
                exit_price=exit_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                position_size_usd=position_size,
                leverage=leverage,
                pattern_tag=pattern_tag,
                psychology_state=psychology_state,
                notes=notes,
                chart_url=chart_url if chart_url else None
            )
            
            if status != 'OPEN' and not trade.closed_at:
                trade.closed_at = timezone.now()
                
            trade.save()
            messages.success(request, f"Trade entry for {symbol} ({trade_type}) saved successfully!")
            return redirect('trade_detail', trade_id=trade.id)
        except ValueError as e:
            messages.error(request, f"Invalid numerical value: {str(e)}")
            
    context = {
        'pattern_choices': PATTERN_TAG_CHOICES,
        'psychology_choices': PSYCHOLOGY_CHOICES,
        'status_choices': TradeEntry._meta.get_field('status').choices,
        'trade_type_choices': TradeEntry._meta.get_field('trade_type').choices,
    }
    return render(request, 'journal/trade_form.html', context)

@login_required
def trade_edit(request, trade_id):
    trade = get_object_or_404(TradeEntry, id=trade_id, user=request.user)
    
    if request.method == 'POST':
        try:
            trade.symbol = request.POST.get('symbol', '').upper().strip()
            trade.trade_type = request.POST.get('trade_type', 'LONG')
            trade.status = request.POST.get('status', 'OPEN')
            
            trade.entry_price = float(request.POST.get('entry_price', trade.entry_price))
            
            exit_price_str = request.POST.get('exit_price', '').strip()
            trade.exit_price = float(exit_price_str) if exit_price_str else None
            
            stop_loss_str = request.POST.get('stop_loss', '').strip()
            trade.stop_loss = float(stop_loss_str) if stop_loss_str else None
            
            take_profit_str = request.POST.get('take_profit', '').strip()
            trade.take_profit = float(take_profit_str) if take_profit_str else None
            
            trade.position_size_usd = float(request.POST.get('position_size_usd', trade.position_size_usd))
            trade.leverage = int(request.POST.get('leverage', trade.leverage))
            
            trade.pattern_tag = request.POST.get('pattern_tag', trade.pattern_tag)
            trade.psychology_state = request.POST.get('psychology_state', trade.psychology_state)
            trade.notes = request.POST.get('notes', trade.notes)
            
            chart_url = request.POST.get('chart_url', '').strip()
            trade.chart_url = chart_url if chart_url else None
            
            if trade.status != 'OPEN' and not trade.closed_at:
                trade.closed_at = timezone.now()
                
            trade.save()
            messages.success(request, f"Trade #{trade.id} ({trade.symbol}) updated successfully.")
            return redirect('trade_detail', trade_id=trade.id)
        except ValueError as e:
            messages.error(request, f"Invalid value: {str(e)}")

    context = {
        'trade': trade,
        'is_edit': True,
        'pattern_choices': PATTERN_TAG_CHOICES,
        'psychology_choices': PSYCHOLOGY_CHOICES,
        'status_choices': TradeEntry._meta.get_field('status').choices,
        'trade_type_choices': TradeEntry._meta.get_field('trade_type').choices,
    }
    return render(request, 'journal/trade_form.html', context)

@login_required
def trade_detail(request, trade_id):
    trade = get_object_or_404(TradeEntry, id=trade_id, user=request.user)
    return render(request, 'journal/trade_detail.html', {'trade': trade})

@login_required
def trade_delete(request, trade_id):
    trade = get_object_or_404(TradeEntry, id=trade_id, user=request.user)
    if request.method == 'POST':
        symbol = trade.symbol
        trade.delete()
        messages.success(request, f"Trade entry for {symbol} deleted.")
        return redirect('trade_list')
    return render(request, 'journal/trade_confirm_delete.html', {'trade': trade})


# ==========================================================
# UNIQUE UNFAIR-ADVANTAGE FEATURES
# ==========================================================

@login_required
def fomo_shield(request):
    """
    Psychology Leak Audit & Tilt Lockout Engine.
    Quantifies exact money lost to emotional states (FOMO, Revenge, Greed, Panic).
    Calculates Psychological Efficiency %, and checks for active Tilt Cooldowns.
    """
    user_trades = TradeEntry.objects.filter(user=request.user).exclude(status='OPEN')
    
    emotional_states = ['FOMO_ENTRY', 'REVENGE_TRADE', 'GREED_OVERLEVERAGED', 'PANIC_CUT', 'EARLY_EXIT']
    disciplined_trades = user_trades.filter(psychology_state='DISCIPLINED')
    emotional_trades = user_trades.filter(psychology_state__in=emotional_states)
    
    disciplined_pnl = disciplined_trades.aggregate(Sum('pnl_usd'))['pnl_usd__sum'] or 0.0
    emotional_pnl = emotional_trades.aggregate(Sum('pnl_usd'))['pnl_usd__sum'] or 0.0
    
    # Calculate exact mistake leak
    mistake_loss = abs(emotional_trades.filter(pnl_usd__lt=0).aggregate(Sum('pnl_usd'))['pnl_usd__sum'] or 0.0)
    
    total_potential_pnl = max(1.0, disciplined_pnl + mistake_loss)
    psychological_efficiency = round(max(0, min(100, (disciplined_pnl / total_potential_pnl) * 100)), 1)
    
    # Breakdown by psychology state
    psychology_stats = []
    for code, label in PSYCHOLOGY_CHOICES:
        state_trades = user_trades.filter(psychology_state=code)
        count = state_trades.count()
        pnl = state_trades.aggregate(Sum('pnl_usd'))['pnl_usd__sum'] or 0.0
        avg_pnl = round(pnl / count, 2) if count > 0 else 0.0
        win_count = state_trades.filter(status='CLOSED_WIN').count()
        wr = round((win_count / count * 100), 1) if count > 0 else 0.0
        
        psychology_stats.append({
            'code': code,
            'label': label,
            'count': count,
            'pnl': round(pnl, 2),
            'abs_pnl': round(abs(pnl), 2),
            'avg_pnl': avg_pnl,
            'win_rate': wr,
        })
    
    # Tilt Check: inspect last 3 closed trades
    last_3 = user_trades.order_by('-created_at')[:3]
    recent_emotional_losses = [t for t in last_3 if t.psychology_state in emotional_states and t.pnl_usd < 0]
    is_tilted = len(recent_emotional_losses) >= 2
    
    context = {
        'disciplined_pnl': round(disciplined_pnl, 2),
        'abs_disciplined_pnl': round(abs(disciplined_pnl), 2),
        'emotional_pnl': round(emotional_pnl, 2),
        'mistake_loss': round(mistake_loss, 2),
        'psychological_efficiency': psychological_efficiency,
        'psychology_stats': psychology_stats,
        'is_tilted': is_tilted,
        'tilt_count': len(recent_emotional_losses),
    }
    return render(request, 'journal/fomo_shield.html', context)

@login_required
def pattern_edge_matrix(request):
    """
    Personal Pattern Expectancy & AI Pre-Trade Edge Simulator.
    Computes user's actual win rate & expectancy for each of the 12 patterns.
    Includes a live setup evaluator scoring prospective trades A+ to F.
    """
    user_trades = TradeEntry.objects.filter(user=request.user).exclude(status='OPEN')
    
    pattern_stats = []
    for tag_code, tag_label in PATTERN_TAG_CHOICES:
        p_trades = user_trades.filter(pattern_tag=tag_code)
        count = p_trades.count()
        if count > 0:
            win_count = p_trades.filter(status='CLOSED_WIN').count()
            win_rate = round((win_count / count) * 100, 1)
            total_pnl = p_trades.aggregate(Sum('pnl_usd'))['pnl_usd__sum'] or 0.0
            avg_pnl = round(total_pnl / count, 2)
            expectancy = avg_pnl
        else:
            win_rate = 0.0
            total_pnl = 0.0
            avg_pnl = 0.0
            expectancy = 0.0
            
        pattern_stats.append({
            'code': tag_code,
            'label': tag_label,
            'count': count,
            'win_rate': win_rate,
            'total_pnl': round(total_pnl, 2),
            'abs_total_pnl': round(abs(total_pnl), 2),
            'expectancy': expectancy
        })
    
    # Pre-Trade Simulator processing
    sim_result = None
    if request.method == 'POST':
        symbol = request.POST.get('sim_symbol', 'SOL/USDT').upper()
        fdv = float(request.POST.get('sim_fdv', 100000000) or 0)
        team_score = int(request.POST.get('sim_team', 7) or 7)
        utility_score = int(request.POST.get('sim_utility', 7) or 7)
        audit = request.POST.get('sim_audit', 'full')
        whale_inflows = request.POST.get('sim_whale', 'no') == 'yes'
        rsi = float(request.POST.get('sim_rsi', 45) or 45)
        hype = request.POST.get('sim_hype', 'medium')
        
        # Calculate AI Edge Rating Score (0-100)
        score = 50
        if team_score >= 8: score += 10
        if utility_score >= 8: score += 10
        if audit == 'full': score += 10
        if whale_inflows: score += 15
        if 35 <= rsi <= 60: score += 10
        if hype == 'high': score += 5
        if fdv > 500000000: score -= 10
        
        score = max(5, min(98, score))
        
        if score >= 85: grade, bg = 'A+', 'success'
        elif score >= 75: grade, bg = 'A', 'success'
        elif score >= 60: grade, bg = 'B', 'info'
        elif score >= 45: grade, bg = 'C', 'warning'
        else: grade, bg = 'D / HIGH RISK', 'danger'
        
        profile = getattr(request.user, 'profile', None)
        user_balance = profile.account_balance if profile else 10000.0
        risk_pct = profile.risk_per_trade_pct if profile else 2.0
        max_risk_usd = round(user_balance * (risk_pct / 100.0), 2)
        
        sim_result = {
            'symbol': symbol,
            'score': score,
            'grade': grade,
            'bg': bg,
            'win_probability': f"{score}%",
            'max_risk_usd': max_risk_usd,
            'rec_position_usd': round(max_risk_usd * 10, 2),
        }

    context = {
        'pattern_stats': pattern_stats,
        'sim_result': sim_result,
        'pattern_choices': PATTERN_TAG_CHOICES,
    }
    return render(request, 'journal/pattern_edge.html', context)

@login_required
def analytics_dashboard(request):
    """
    Advanced Quantitative Performance Analytics.
    Equity curves, win/loss distributions, expectancy calculations.
    """
    user_trades = TradeEntry.objects.filter(user=request.user).order_by('created_at')
    closed_trades = user_trades.exclude(status='OPEN')
    
    # Cumulative Equity Curve calculation
    dates = []
    equity_curve = []
    current_equity = getattr(request.user.profile, 'account_balance', 10000.0)
    running_balance = current_equity
    
    dates.append(timezone.now().strftime("%Y-%m-%d"))
    equity_curve.append(running_balance)
    
    for t in closed_trades:
        running_balance += t.pnl_usd
        dates.append(t.closed_at.strftime("%Y-%m-%d") if t.closed_at else t.created_at.strftime("%Y-%m-%d"))
        equity_curve.append(round(running_balance, 2))
        
    # Plotly Equity Curve Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=equity_curve,
        mode='lines+markers',
        name='Account Balance',
        line=dict(color='#2563eb', width=3),
        marker=dict(size=6, color='#10b981')
    ))
    fig.update_layout(
        title="Account Equity Growth Curve ($)",
        template="plotly_white",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(family="Inter, sans-serif", color="#0f172a")
    )
    equity_chart = fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    # Win / Loss Distribution Donut
    win_count = closed_trades.filter(status='CLOSED_WIN').count()
    loss_count = closed_trades.filter(status='CLOSED_LOSS').count()
    breakeven_count = closed_trades.filter(status='CLOSED_BREAKEVEN').count()
    
    fig_donut = go.Figure(data=[go.Pie(
        labels=['Wins', 'Losses', 'Breakeven'],
        values=[win_count, loss_count, breakeven_count],
        hole=.5,
        marker_colors=['#10b981', '#ef4444', '#f59e0b']
    )])
    fig_donut.update_layout(
        title="Win / Loss Ratio",
        template="plotly_white",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(family="Inter, sans-serif", color="#0f172a")
    )
    win_loss_chart = fig_donut.to_html(full_html=False, include_plotlyjs='cdn')

    context = {
        'equity_chart': equity_chart,
        'win_loss_chart': win_loss_chart,
        'total_closed': closed_trades.count(),
        'win_count': win_count,
        'loss_count': loss_count,
    }
    return render(request, 'journal/analytics.html', context)

@login_required
def generate_demo_trades(request):
    """
    One-click demo trade generator to populate rich sample data for instant demonstration.
    """
    symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'NEAR/USDT', 'SUI/USDT', 'AVAX/USDT', 'FET/USDT', 'PEPE/USDT']
    patterns_list = [p[0] for p in PATTERN_TAG_CHOICES]
    psych_list = [p[0] for p in PSYCHOLOGY_CHOICES]
    
    now = timezone.now()
    
    # Create 12 realistic past trades
    for i in range(12):
        symbol = random.choice(symbols)
        trade_type = random.choice(['LONG', 'SHORT'])
        entry = random.uniform(10, 500) if 'SOL' in symbol or 'AVAX' in symbol else (random.uniform(2000, 3500) if 'ETH' in symbol else random.uniform(50000, 68000))
        
        # 65% win probability for demo data
        is_win = random.random() < 0.65
        status = 'CLOSED_WIN' if is_win else 'CLOSED_LOSS'
        
        if is_win:
            exit_price = entry * (1 + random.uniform(0.04, 0.15)) if trade_type == 'LONG' else entry * (1 - random.uniform(0.04, 0.15))
            psych = random.choice(['DISCIPLINED', 'DISCIPLINED', 'DISCIPLINED', 'EARLY_EXIT'])
        else:
            exit_price = entry * (1 - random.uniform(0.03, 0.08)) if trade_type == 'LONG' else entry * (1 + random.uniform(0.03, 0.08))
            psych = random.choice(['FOMO_ENTRY', 'REVENGE_TRADE', 'GREED_OVERLEVERAGED', 'PANIC_CUT', 'DISCIPLINED'])
            
        stop_loss = entry * 0.95 if trade_type == 'LONG' else entry * 1.05
        take_profit = entry * 1.12 if trade_type == 'LONG' else entry * 0.88
        
        past_days = random.randint(1, 30)
        created_time = now - timedelta(days=past_days, hours=random.randint(1, 12))
        closed_time = created_time + timedelta(hours=random.randint(2, 48))
        
        trade = TradeEntry.objects.create(
            user=request.user,
            symbol=symbol,
            trade_type=trade_type,
            status=status,
            entry_price=round(entry, 2),
            exit_price=round(exit_price, 2),
            stop_loss=round(stop_loss, 2),
            take_profit=round(take_profit, 2),
            position_size_usd=random.choice([500, 1000, 1500, 2500]),
            leverage=random.choice([1, 2, 3, 5]),
            pattern_tag=random.choice(patterns_list),
            psychology_state=psych,
            notes="Sample demo trade generated for quant & psychology audit testing.",
            created_at=created_time,
            closed_at=closed_time
        )
        
    messages.success(request, "🎉 12 realistic sample trades generated! Explore your Dashboard, FOMO Shield, and Pattern Edge analytics.")
    return redirect('journal_dashboard')