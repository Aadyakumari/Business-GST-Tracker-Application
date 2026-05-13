# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import numpy as np
# from sklearn.linear_model import LinearRegression
# import json

# app = Flask(__name__)
# CORS(app)

# @app.route('/predict', methods=['POST'])
# def predict_gst():
#     try:
#         data = request.json
#         invoices = data.get('invoices', [])

#         if len(invoices) < 2:
#             return jsonify({
#                 'predicted_sales': 0,
#                 'predicted_gst': 0,
#                 'message': 'Not enough data to predict. Add more invoices!'
#             })

#         # Prepare data
#         sales_by_month = {}
#         gst_by_month = {}

#         for inv in invoices:
#             date = inv['date'][:7]  # Get YYYY-MM
#             if inv['type'] == 'SALE':
#                 sales_by_month[date] = sales_by_month.get(date, 0) + inv['amount']
#                 gst_by_month[date] = gst_by_month.get(date, 0) + inv['gstAmount']

#         if len(sales_by_month) < 2:
#             return jsonify({
#                 'predicted_sales': round(sum(sales_by_month.values()) * 1.1, 2),
#                 'predicted_gst': round(sum(gst_by_month.values()) * 1.1, 2),
#                 'message': 'Prediction based on growth trend'
#             })

#         # Sort by month
#         months = sorted(sales_by_month.keys())
#         X = np.array(range(len(months))).reshape(-1, 1)
#         y_sales = np.array([sales_by_month[m] for m in months])
#         y_gst = np.array([gst_by_month[m] for m in months])

#         # Train model
#         model_sales = LinearRegression()
#         model_sales.fit(X, y_sales)

#         model_gst = LinearRegression()
#         model_gst.fit(X, y_gst)

#         # Predict next month
#         next_month = np.array([[len(months)]])
#         predicted_sales = max(0, model_sales.predict(next_month)[0])
#         predicted_gst = max(0, model_gst.predict(next_month)[0])

#         return jsonify({
#             'predicted_sales': round(float(predicted_sales), 2),
#             'predicted_gst': round(float(predicted_gst), 2),
#             'months_analyzed': len(months),
#             'message': f'Based on {len(months)} months of data'
#         })

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/anomaly', methods=['POST'])
# def detect_anomaly():
#     try:
#         data = request.json
#         invoices = data.get('invoices', [])

#         if len(invoices) < 3:
#             return jsonify({'anomalies': [], 'message': 'Need more invoices for anomaly detection'})

#         amounts = [inv['amount'] for inv in invoices]
#         mean = np.mean(amounts)
#         std = np.std(amounts)

#         anomalies = []
#         for inv in invoices:
#             z_score = abs(inv['amount'] - mean) / std if std > 0 else 0
#             if z_score > 2:
#                 anomalies.append({
#                     'id': inv['id'],
#                     'partyName': inv['partyName'],
#                     'amount': inv['amount'],
#                     'reason': f'Unusual amount (₹{inv["amount"]}) compared to average (₹{round(mean, 2)})'
#                 })

#         return jsonify({
#             'anomalies': anomalies,
#             'total_invoices': len(invoices),
#             'average_amount': round(mean, 2)
#         })

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# if __name__ == '__main__':
#     app.run(port=5001, debug=True, host='0.0.0.0')















# from flask import Flask, request, jsonify, send_file
# from flask_cors import CORS
# import numpy as np
# from sklearn.linear_model import LinearRegression
# from sklearn.preprocessing import PolynomialFeatures
# from sklearn.pipeline import make_pipeline
# from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
# import matplotlib
# matplotlib.use('Agg')  # Non-interactive backend — required for server
# import matplotlib.pyplot as plt
# import matplotlib.patches as mpatches
# import io
# import base64
# import json
# from scipy import stats
 
# app = Flask(__name__)
# CORS(app)
 
# # ─────────────────────────────────────────────
# # UTILITY: Prepare monthly sales data from invoices
# # ─────────────────────────────────────────────
# def prepare_monthly_data(invoices, invoice_type='SALE'):
#     sales_by_month = {}
#     gst_by_month = {}
#     for inv in invoices:
#         if inv['type'] == invoice_type:
#             date = inv['date'][:7]
#             sales_by_month[date] = sales_by_month.get(date, 0) + inv['amount']
#             gst_by_month[date]   = gst_by_month.get(date, 0)   + inv['gstAmount']
#     months   = sorted(sales_by_month.keys())
#     y_sales  = np.array([sales_by_month[m] for m in months])
#     y_gst    = np.array([gst_by_month[m]   for m in months])
#     X        = np.arange(len(months)).reshape(-1, 1)
#     return X, y_sales, y_gst, months
 
 
# # ─────────────────────────────────────────────
# # EXISTING ROUTE 1 — /predict (IMPROVED — adds R², MAE, RMSE)
# # ─────────────────────────────────────────────
# @app.route('/predict', methods=['POST'])
# def predict_gst():
#     try:
#         data     = request.json
#         invoices = data.get('invoices', [])
 
#         if len(invoices) < 2:
#             return jsonify({
#                 'predicted_sales': 0,
#                 'predicted_gst':   0,
#                 'message':         'Not enough data to predict. Add more invoices!'
#             })
 
#         X, y_sales, y_gst, months = prepare_monthly_data(invoices)
 
#         if len(months) < 2:
#             return jsonify({
#                 'predicted_sales': round(float(y_sales.sum()) * 1.1, 2),
#                 'predicted_gst':   round(float(y_gst.sum())   * 1.1, 2),
#                 'message':         'Prediction based on growth trend'
#             })
 
#         # Train models
#         model_sales = LinearRegression().fit(X, y_sales)
#         model_gst   = LinearRegression().fit(X, y_gst)
 
#         # Predict next month
#         next_X          = np.array([[len(months)]])
#         predicted_sales = max(0, model_sales.predict(next_X)[0])
#         predicted_gst   = max(0, model_gst.predict(next_X)[0])
 
#         # Model evaluation metrics
#         y_sales_pred = model_sales.predict(X)
#         r2   = round(float(r2_score(y_sales, y_sales_pred)), 4)
#         mae  = round(float(mean_absolute_error(y_sales, y_sales_pred)), 2)
#         rmse = round(float(np.sqrt(mean_squared_error(y_sales, y_sales_pred))), 2)
 
#         # Month-over-month growth rate
#         growth_rate = 0
#         if len(y_sales) >= 2:
#             growth_rate = round(
#                 ((y_sales[-1] - y_sales[-2]) / y_sales[-2]) * 100, 2
#             ) if y_sales[-2] != 0 else 0
 
#         return jsonify({
#             'predicted_sales':   round(float(predicted_sales), 2),
#             'predicted_gst':     round(float(predicted_gst), 2),
#             'months_analyzed':   len(months),
#             'message':           f'Based on {len(months)} months of data',
#             'model_accuracy': {
#                 'r2_score':          r2,
#                 'mae':               mae,
#                 'rmse':              rmse,
#                 'interpretation':    'Good fit' if r2 > 0.8 else 'Moderate fit' if r2 > 0.5 else 'Limited data — accuracy improves with more months'
#             },
#             'growth_rate_percent': growth_rate,
#             'trend':               'Increasing' if model_sales.coef_[0] > 0 else 'Decreasing'
#         })
 
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
 
 
# # ─────────────────────────────────────────────
# # EXISTING ROUTE 2 — /anomaly (IMPROVED — adds risk score 0-100)
# # ─────────────────────────────────────────────
# @app.route('/anomaly', methods=['POST'])
# def detect_anomaly():
#     try:
#         data     = request.json
#         invoices = data.get('invoices', [])
 
#         if len(invoices) < 3:
#             return jsonify({
#                 'anomalies': [],
#                 'message':   'Need more invoices for anomaly detection'
#             })
 
#         amounts = np.array([inv['amount'] for inv in invoices])
#         mean    = float(np.mean(amounts))
#         std     = float(np.std(amounts))
#         q1      = float(np.percentile(amounts, 25))
#         q3      = float(np.percentile(amounts, 75))
#         iqr     = q3 - q1
 
#         anomalies = []
#         scored_invoices = []
 
#         for inv in invoices:
#             z_score    = abs(inv['amount'] - mean) / std if std > 0 else 0
#             iqr_score  = abs(inv['amount'] - mean) / iqr  if iqr > 0 else 0
 
#             # Risk score 0–100 (combining Z-score and IQR)
#             raw_risk   = min(100, round((z_score * 25) + (iqr_score * 10), 1))
#             risk_level = (
#                 'Critical' if raw_risk >= 75 else
#                 'High'     if raw_risk >= 50 else
#                 'Medium'   if raw_risk >= 25 else
#                 'Low'
#             )
 
#             scored_invoices.append({
#                 'id':         inv['id'],
#                 'partyName':  inv['partyName'],
#                 'amount':     inv['amount'],
#                 'risk_score': raw_risk,
#                 'risk_level': risk_level,
#                 'z_score':    round(z_score, 2)
#             })
 
#             if z_score > 2:
#                 anomalies.append({
#                     'id':        inv['id'],
#                     'partyName': inv['partyName'],
#                     'amount':    inv['amount'],
#                     'risk_score': raw_risk,
#                     'risk_level': risk_level,
#                     'reason':    f'Unusual amount (₹{inv["amount"]:,}) compared to average (₹{round(mean, 2):,})',
#                     'z_score':   round(z_score, 2)
#                 })
 
#         return jsonify({
#             'anomalies':       anomalies,
#             'all_invoices_scored': sorted(scored_invoices, key=lambda x: x['risk_score'], reverse=True),
#             'total_invoices':  len(invoices),
#             'average_amount':  round(mean, 2),
#             'std_deviation':   round(std, 2),
#             'statistics': {
#                 'mean': round(mean, 2),
#                 'std':  round(std,  2),
#                 'q1':   round(q1,   2),
#                 'q3':   round(q3,   2),
#                 'iqr':  round(iqr,  2)
#             }
#         })
 
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
 
 
# # ─────────────────────────────────────────────
# # NEW ROUTE 3 — /graph
# # Predicted vs Actual sales + confidence band
# # R², MAE, RMSE printed on graph
# # Returns base64 PNG — display directly in frontend
# # ─────────────────────────────────────────────
# @app.route('/graph', methods=['POST'])
# def generate_graph():
#     try:
#         data     = request.json
#         invoices = data.get('invoices', [])
 
#         X, y_sales, _, months = prepare_monthly_data(invoices)
 
#         if len(months) < 2:
#             return jsonify({'error': 'Need at least 2 months of sales data'}), 400
 
#         # Train model
#         model      = LinearRegression().fit(X, y_sales)
#         y_pred     = model.predict(X)
#         next_X     = np.array([[len(months)]])
#         next_pred  = max(0, model.predict(next_X)[0])
 
#         # Metrics
#         r2   = r2_score(y_sales, y_pred)
#         mae  = mean_absolute_error(y_sales, y_pred)
#         rmse = np.sqrt(mean_squared_error(y_sales, y_pred))
 
#         # Confidence interval using residual std
#         residuals  = y_sales - y_pred
#         res_std    = np.std(residuals)
#         t_val      = stats.t.ppf(0.975, df=max(1, len(months) - 2))
#         ci         = t_val * res_std
 
#         # Extended X for plotting (include next month)
#         X_plot     = np.arange(len(months) + 1).reshape(-1, 1)
#         y_plot     = model.predict(X_plot)
#         upper      = y_plot + ci
#         lower      = np.maximum(0, y_plot - ci)
 
#         # ── Plot ───────────────────────────────
#         fig, ax = plt.subplots(figsize=(10, 5.5))
#         fig.patch.set_facecolor('#0F172A')
#         ax.set_facecolor('#1E293B')
 
#         month_labels = months + [f'Next Month\n(Predicted)']
#         x_ticks      = np.arange(len(month_labels))
 
#         # Confidence band
#         ax.fill_between(x_ticks, lower, upper,
#                         alpha=0.18, color='#38BDF8', label='95% Confidence Band')
 
#         # Regression line extended
#         ax.plot(x_ticks, y_plot, '--', color='#38BDF8',
#                 linewidth=1.8, label='Regression Line', zorder=3)
 
#         # Actual values
#         ax.plot(x_ticks[:len(months)], y_sales,
#                 'o-', color='#22C55E', linewidth=2.5,
#                 markersize=8, label='Actual Sales', zorder=5)
 
#         # Predicted actual points
#         ax.plot(x_ticks[:len(months)], y_pred,
#                 's', color='#FACC15', markersize=6,
#                 label='Model Fitted Values', zorder=4)
 
#         # Next month prediction point
#         ax.plot(x_ticks[-1], next_pred,
#                 '*', color='#F97316', markersize=16,
#                 label=f'Next Month Prediction: ₹{next_pred:,.0f}', zorder=6)
 
#         # Vertical separator
#         ax.axvline(x=len(months) - 0.5, color='#475569',
#                    linestyle=':', linewidth=1.2, alpha=0.7)
#         ax.text(len(months) - 0.45, ax.get_ylim()[1] * 0.95,
#                 'Forecast →', color='#94A3B8', fontsize=8)
 
#         # Metrics box
#         metrics_text = (
#             f'R² Score : {r2:.4f}\n'
#             f'MAE      : ₹{mae:,.0f}\n'
#             f'RMSE     : ₹{rmse:,.0f}'
#         )
#         ax.text(0.02, 0.97, metrics_text,
#                 transform=ax.transAxes, fontsize=9,
#                 verticalalignment='top',
#                 bbox=dict(boxstyle='round,pad=0.5',
#                           facecolor='#0F172A', edgecolor='#38BDF8',
#                           alpha=0.85),
#                 color='#E2E8F0', fontfamily='monospace')
 
#         # Formatting
#         ax.set_xticks(x_ticks)
#         ax.set_xticklabels(month_labels, color='#CBD5E1', fontsize=9)
#         ax.yaxis.set_major_formatter(
#             plt.FuncFormatter(lambda v, _: f'₹{v/1e5:.1f}L' if v >= 1e5 else f'₹{v:,.0f}')
#         )
#         ax.tick_params(colors='#CBD5E1')
#         ax.set_title('Sales Forecast — Predicted vs Actual with Confidence Interval',
#                      color='#F1F5F9', fontsize=13, fontweight='bold', pad=14)
#         ax.set_xlabel('Month', color='#94A3B8', fontsize=10)
#         ax.set_ylabel('Sales (₹)', color='#94A3B8', fontsize=10)
#         ax.grid(True, linestyle='--', alpha=0.2, color='#475569')
#         ax.spines[:].set_color('#334155')
 
#         legend = ax.legend(facecolor='#1E293B', edgecolor='#334155',
#                            labelcolor='#E2E8F0', fontsize=8.5, loc='upper left',
#                            bbox_to_anchor=(0.0, 0.78))
 
#         plt.tight_layout()
 
#         # Convert to base64
#         buf = io.BytesIO()
#         plt.savefig(buf, format='png', dpi=130,
#                     bbox_inches='tight', facecolor='#0F172A')
#         buf.seek(0)
#         img_base64 = base64.b64encode(buf.read()).decode('utf-8')
#         plt.close()
 
#         return jsonify({
#             'graph':   img_base64,
#             'metrics': {
#                 'r2_score': round(r2,   4),
#                 'mae':      round(mae,  2),
#                 'rmse':     round(rmse, 2)
#             },
#             'next_month_prediction': round(float(next_pred), 2),
#             'confidence_interval':   round(float(ci), 2)
#         })
 
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
 
 
# # ─────────────────────────────────────────────
# # NEW ROUTE 4 — /model-comparison
# # Linear vs Polynomial Regression — which fits better
# # Returns comparison graph + winner
# # ─────────────────────────────────────────────
# @app.route('/model-comparison', methods=['POST'])
# def model_comparison():
#     try:
#         data     = request.json
#         invoices = data.get('invoices', [])
 
#         X, y_sales, _, months = prepare_monthly_data(invoices)
 
#         if len(months) < 2:
#             return jsonify({'error': 'Need at least 2 months of data'}), 400
 
#         # Train both models
#         lr_model   = LinearRegression().fit(X, y_sales)
#         poly_model = make_pipeline(
#             PolynomialFeatures(degree=2), LinearRegression()
#         ).fit(X, y_sales)
 
#         lr_pred   = lr_model.predict(X)
#         poly_pred = poly_model.predict(X)
 
#         lr_r2   = r2_score(y_sales, lr_pred)
#         poly_r2 = r2_score(y_sales, poly_pred)
#         lr_rmse = np.sqrt(mean_squared_error(y_sales, lr_pred))
#         poly_rmse = np.sqrt(mean_squared_error(y_sales, poly_pred))
 
#         # Next month
#         next_X      = np.array([[len(months)]])
#         lr_next     = max(0, lr_model.predict(next_X)[0])
#         poly_next   = max(0, poly_model.predict(next_X)[0])
 
#         # Plot
#         fig, ax = plt.subplots(figsize=(10, 5.5))
#         fig.patch.set_facecolor('#0F172A')
#         ax.set_facecolor('#1E293B')
 
#         x_ticks = np.arange(len(months))
 
#         ax.plot(x_ticks, y_sales, 'o-', color='#22C55E',
#                 linewidth=2.5, markersize=9, label='Actual Sales', zorder=5)
#         ax.plot(x_ticks, lr_pred, '--', color='#38BDF8',
#                 linewidth=2, label=f'Linear Regression  (R²={lr_r2:.3f})', zorder=4)
#         ax.plot(x_ticks, poly_pred, '--', color='#F97316',
#                 linewidth=2, label=f'Polynomial Degree-2 (R²={poly_r2:.3f})', zorder=4)
 
#         winner = 'Linear Regression' if lr_r2 >= poly_r2 else 'Polynomial Regression'
#         winner_color = '#38BDF8' if lr_r2 >= poly_r2 else '#F97316'
 
#         ax.set_title(f'Model Comparison — Winner: {winner}',
#                      color='#F1F5F9', fontsize=13, fontweight='bold', pad=14)
 
#         comparison_text = (
#             f'Linear     →  R²={lr_r2:.3f}  RMSE=₹{lr_rmse:,.0f}\n'
#             f'Polynomial →  R²={poly_r2:.3f}  RMSE=₹{poly_rmse:,.0f}\n'
#             f'Best Model →  {winner}'
#         )
#         ax.text(0.02, 0.97, comparison_text,
#                 transform=ax.transAxes, fontsize=9,
#                 verticalalignment='top',
#                 bbox=dict(boxstyle='round,pad=0.5',
#                           facecolor='#0F172A', edgecolor=winner_color, alpha=0.85),
#                 color='#E2E8F0', fontfamily='monospace')
 
#         ax.set_xticks(x_ticks)
#         ax.set_xticklabels(months, color='#CBD5E1', fontsize=9)
#         ax.yaxis.set_major_formatter(
#             plt.FuncFormatter(lambda v, _: f'₹{v/1e5:.1f}L' if v >= 1e5 else f'₹{v:,.0f}')
#         )
#         ax.tick_params(colors='#CBD5E1')
#         ax.set_xlabel('Month', color='#94A3B8', fontsize=10)
#         ax.set_ylabel('Sales (₹)', color='#94A3B8', fontsize=10)
#         ax.grid(True, linestyle='--', alpha=0.2, color='#475569')
#         ax.spines[:].set_color('#334155')
#         ax.legend(facecolor='#1E293B', edgecolor='#334155',
#                   labelcolor='#E2E8F0', fontsize=9)
 
#         plt.tight_layout()
 
#         buf = io.BytesIO()
#         plt.savefig(buf, format='png', dpi=130,
#                     bbox_inches='tight', facecolor='#0F172A')
#         buf.seek(0)
#         img_base64 = base64.b64encode(buf.read()).decode('utf-8')
#         plt.close()
 
#         return jsonify({
#             'graph':  img_base64,
#             'winner': winner,
#             'models': {
#                 'linear':     {'r2': round(lr_r2, 4),   'rmse': round(lr_rmse, 2),   'next_prediction': round(float(lr_next), 2)},
#                 'polynomial': {'r2': round(poly_r2, 4), 'rmse': round(poly_rmse, 2), 'next_prediction': round(float(poly_next), 2)}
#             }
#         })
 
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
 
 
# # ─────────────────────────────────────────────
# # NEW ROUTE 5 — /insights
# # Month-over-month growth, GST trend, peak month
# # ─────────────────────────────────────────────
# @app.route('/insights', methods=['POST'])
# def business_insights():
#     try:
#         data     = request.json
#         invoices = data.get('invoices', [])
 
#         X, y_sales, y_gst, months = prepare_monthly_data(invoices)
 
#         if len(months) < 2:
#             return jsonify({'error': 'Need at least 2 months of data'}), 400
 
#         # Growth rates
#         mom_growth = []
#         for i in range(1, len(y_sales)):
#             if y_sales[i - 1] != 0:
#                 growth = ((y_sales[i] - y_sales[i - 1]) / y_sales[i - 1]) * 100
#                 mom_growth.append(round(growth, 2))
 
#         avg_growth    = round(float(np.mean(mom_growth)), 2) if mom_growth else 0
#         peak_month    = months[int(np.argmax(y_sales))]
#         peak_sales    = float(np.max(y_sales))
#         gst_ratio     = round(float(np.mean(y_gst / y_sales * 100)), 2) if y_sales.sum() > 0 else 0
 
#         # GST trend
#         gst_model     = LinearRegression().fit(X, y_gst)
#         gst_trend     = 'Increasing' if gst_model.coef_[0] > 0 else 'Decreasing'
 
#         # Purchase analysis
#         Xp, y_purchase, y_gst_purchase, purchase_months = prepare_monthly_data(invoices, 'PURCHASE')
#         purchase_ratio = round(float(y_purchase.sum() / y_sales.sum() * 100), 2) if y_sales.sum() > 0 else 0
 
#         # Plot — monthly sales + GST bar chart
#         fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
#         fig.patch.set_facecolor('#0F172A')
 
#         x_ticks = np.arange(len(months))
 
#         # Left — Sales trend
#         ax1.set_facecolor('#1E293B')
#         bars = ax1.bar(x_ticks, y_sales, color='#3B82F6', alpha=0.85,
#                        label='Monthly Sales')
#         ax1.plot(x_ticks, LinearRegression().fit(X, y_sales).predict(X),
#                  '--', color='#22C55E', linewidth=2, label='Trend Line')
#         ax1.set_title('Monthly Sales Trend', color='#F1F5F9',
#                       fontsize=11, fontweight='bold')
#         ax1.set_xticks(x_ticks)
#         ax1.set_xticklabels(months, color='#CBD5E1', fontsize=8, rotation=15)
#         ax1.yaxis.set_major_formatter(
#             plt.FuncFormatter(lambda v, _: f'₹{v/1e5:.1f}L' if v >= 1e5 else f'₹{v:,.0f}')
#         )
#         ax1.tick_params(colors='#CBD5E1')
#         ax1.set_facecolor('#1E293B')
#         ax1.grid(True, linestyle='--', alpha=0.2, color='#475569')
#         ax1.spines[:].set_color('#334155')
#         ax1.legend(facecolor='#1E293B', edgecolor='#334155',
#                    labelcolor='#E2E8F0', fontsize=8)
 
#         # Right — GST collected per month
#         ax2.set_facecolor('#1E293B')
#         ax2.bar(x_ticks, y_gst, color='#F59E0B', alpha=0.85, label='GST Collected')
#         ax2.set_title('Monthly GST Collection Trend', color='#F1F5F9',
#                       fontsize=11, fontweight='bold')
#         ax2.set_xticks(x_ticks)
#         ax2.set_xticklabels(months, color='#CBD5E1', fontsize=8, rotation=15)
#         ax2.yaxis.set_major_formatter(
#             plt.FuncFormatter(lambda v, _: f'₹{v/1e5:.1f}L' if v >= 1e5 else f'₹{v:,.0f}')
#         )
#         ax2.tick_params(colors='#CBD5E1')
#         ax2.grid(True, linestyle='--', alpha=0.2, color='#475569')
#         ax2.spines[:].set_color('#334155')
#         ax2.legend(facecolor='#1E293B', edgecolor='#334155',
#                    labelcolor='#E2E8F0', fontsize=8)
 
#         plt.suptitle('Business Intelligence Dashboard',
#                      color='#F1F5F9', fontsize=13, fontweight='bold', y=1.01)
#         plt.tight_layout()
 
#         buf = io.BytesIO()
#         plt.savefig(buf, format='png', dpi=130,
#                     bbox_inches='tight', facecolor='#0F172A')
#         buf.seek(0)
#         img_base64 = base64.b64encode(buf.read()).decode('utf-8')
#         plt.close()
 
#         return jsonify({
#             'graph': img_base64,
#             'insights': {
#                 'average_monthly_growth_percent': avg_growth,
#                 'peak_sales_month':               peak_month,
#                 'peak_sales_amount':              round(peak_sales, 2),
#                 'effective_gst_rate_percent':     gst_ratio,
#                 'gst_collection_trend':           gst_trend,
#                 'purchase_to_sales_ratio_percent':purchase_ratio,
#                 'mom_growth_rates':               mom_growth,
#                 'total_months_analyzed':          len(months)
#             }
#         })
 
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
 
 
# # ─────────────────────────────────────────────────────
# # NEW ROUTE 6 — /anomaly-graph
# # Risk score bar chart for all invoices
# # ─────────────────────────────────────────────────────
# @app.route('/anomaly-graph', methods=['POST'])
# def anomaly_graph():
#     try:
#         data     = request.json
#         invoices = data.get('invoices', [])
 
#         if len(invoices) < 3:
#             return jsonify({'error': 'Need at least 3 invoices'}), 400
 
#         amounts = np.array([inv['amount'] for inv in invoices])
#         mean    = np.mean(amounts)
#         std     = np.std(amounts)
#         iqr     = np.percentile(amounts, 75) - np.percentile(amounts, 25)
 
#         names, scores, colors_bar = [], [], []
#         for inv in invoices:
#             z     = abs(inv['amount'] - mean) / std  if std  > 0 else 0
#             iq    = abs(inv['amount'] - mean) / iqr  if iqr  > 0 else 0
#             score = min(100, round((z * 25) + (iq * 10), 1))
#             names.append(inv['partyName'][:12])
#             scores.append(score)
#             colors_bar.append(
#                 '#EF4444' if score >= 75 else
#                 '#F97316' if score >= 50 else
#                 '#FACC15' if score >= 25 else
#                 '#22C55E'
#             )
 
#         fig, ax = plt.subplots(figsize=(10, 5))
#         fig.patch.set_facecolor('#0F172A')
#         ax.set_facecolor('#1E293B')
 
#         bars = ax.barh(names, scores, color=colors_bar, alpha=0.88, height=0.55)
 
#         # Score labels
#         for bar, score in zip(bars, scores):
#             ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
#                     f'{score}', va='center', ha='left',
#                     color='#E2E8F0', fontsize=9, fontweight='bold')
 
#         # Threshold lines
#         ax.axvline(75, color='#EF4444', linestyle='--', linewidth=1.2, alpha=0.7, label='Critical (75)')
#         ax.axvline(50, color='#F97316', linestyle='--', linewidth=1.2, alpha=0.7, label='High (50)')
#         ax.axvline(25, color='#FACC15', linestyle='--', linewidth=1.2, alpha=0.7, label='Medium (25)')
 
#         # Legend patches
#         legend_items = [
#             mpatches.Patch(color='#EF4444', label='Critical  ≥75'),
#             mpatches.Patch(color='#F97316', label='High      ≥50'),
#             mpatches.Patch(color='#FACC15', label='Medium  ≥25'),
#             mpatches.Patch(color='#22C55E', label='Low       <25'),
#         ]
#         ax.legend(handles=legend_items, facecolor='#1E293B',
#                   edgecolor='#334155', labelcolor='#E2E8F0', fontsize=8.5)
 
#         ax.set_xlim(0, 115)
#         ax.set_xlabel('Risk Score (0 = Safe · 100 = Critical)', color='#94A3B8', fontsize=10)
#         ax.set_title('Invoice Risk Scoring — Anomaly Detection',
#                      color='#F1F5F9', fontsize=13, fontweight='bold', pad=12)
#         ax.tick_params(colors='#CBD5E1')
#         ax.grid(True, axis='x', linestyle='--', alpha=0.2, color='#475569')
#         ax.spines[:].set_color('#334155')
 
#         plt.tight_layout()
 
#         buf = io.BytesIO()
#         plt.savefig(buf, format='png', dpi=130,
#                     bbox_inches='tight', facecolor='#0F172A')
#         buf.seek(0)
#         img_base64 = base64.b64encode(buf.read()).decode('utf-8')
#         plt.close()
 
#         return jsonify({'graph': img_base64})
 
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
 
 
# if __name__ == '__main__':
#     app.run(port=5001, debug=True, host='0.0.0.0')

































# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import numpy as np
# from sklearn.linear_model import LinearRegression
# from sklearn.preprocessing import PolynomialFeatures
# from sklearn.pipeline import make_pipeline
# from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
# import matplotlib
# matplotlib.use('Agg')
# import matplotlib.pyplot as plt
# import matplotlib.patches as mpatches
# import io
# import base64
# from scipy import stats

# app = Flask(__name__)
# CORS(app)

# # ── Color theme — white background, dark text ──────────────
# BG_FIG   = '#FFFFFF'   # figure background
# BG_AX    = '#F8F9FA'   # axes background
# C_GRID   = '#DEE2E6'   # grid lines
# C_SPINE  = '#ADB5BD'   # axis borders
# C_TITLE  = '#1E293B'   # title text
# C_LABEL  = '#444444'   # axis labels
# C_TICK   = '#333333'   # tick labels
# C_TEXT   = '#111111'   # general text
# C_BOX_BG = '#F1F5F9'   # metrics box background
# C_BOX_ED = '#3B82F6'   # metrics box border

# # ── Chart colors ───────────────────────────────────────────
# C_GREEN  = '#16A34A'
# C_BLUE   = '#2563EB'
# C_ORANGE = '#EA580C'
# C_YELLOW = '#CA8A04'
# C_RED    = '#DC2626'
# C_TEAL   = '#0891B2'
# C_PURPLE = '#7C3AED'
# C_AMBER  = '#D97706'


# def prepare_monthly_data(invoices, invoice_type='SALE'):
#     sales_by_month = {}
#     gst_by_month   = {}
#     for inv in invoices:
#         if inv['type'] == invoice_type:
#             date = inv['date'][:7]
#             sales_by_month[date] = sales_by_month.get(date, 0) + inv['amount']
#             gst_by_month[date]   = gst_by_month.get(date, 0)   + inv['gstAmount']
#     months  = sorted(sales_by_month.keys())
#     y_sales = np.array([sales_by_month[m] for m in months])
#     y_gst   = np.array([gst_by_month[m]   for m in months])
#     X       = np.arange(len(months)).reshape(-1, 1)
#     return X, y_sales, y_gst, months


# # ─────────────────────────────────────────────
# # ROUTE 1 — /predict
# # ─────────────────────────────────────────────
# @app.route('/predict', methods=['POST'])
# def predict_gst():
#     try:
#         data     = request.json
#         invoices = data.get('invoices', [])

#         if len(invoices) < 2:
#             return jsonify({
#                 'predicted_sales': 0,
#                 'predicted_gst':   0,
#                 'message':         'Not enough data to predict. Add more invoices!'
#             })

#         X, y_sales, y_gst, months = prepare_monthly_data(invoices)

#         if len(months) < 2:
#             return jsonify({
#                 'predicted_sales': round(float(y_sales.sum()) * 1.1, 2),
#                 'predicted_gst':   round(float(y_gst.sum())   * 1.1, 2),
#                 'message':         'Prediction based on growth trend'
#             })

#         model_sales = LinearRegression().fit(X, y_sales)
#         model_gst   = LinearRegression().fit(X, y_gst)

#         next_X          = np.array([[len(months)]])
#         predicted_sales = max(0, model_sales.predict(next_X)[0])
#         predicted_gst   = max(0, model_gst.predict(next_X)[0])

#         y_sales_pred = model_sales.predict(X)
#         r2   = round(float(r2_score(y_sales, y_sales_pred)), 4)
#         mae  = round(float(mean_absolute_error(y_sales, y_sales_pred)), 2)
#         rmse = round(float(np.sqrt(mean_squared_error(y_sales, y_sales_pred))), 2)

#         growth_rate = 0
#         if len(y_sales) >= 2 and y_sales[-2] != 0:
#             growth_rate = round(((y_sales[-1] - y_sales[-2]) / y_sales[-2]) * 100, 2)

#         return jsonify({
#             'predicted_sales': round(float(predicted_sales), 2),
#             'predicted_gst':   round(float(predicted_gst), 2),
#             'months_analyzed': len(months),
#             'message':         f'Based on {len(months)} months of data',
#             'model_accuracy': {
#                 'r2_score':       r2,
#                 'mae':            mae,
#                 'rmse':           rmse,
#                 'interpretation': 'Good fit' if r2 > 0.8 else 'Moderate fit' if r2 > 0.5 else 'Limited data — accuracy improves with more months'
#             },
#             'growth_rate_percent': growth_rate,
#             'trend': 'Increasing' if model_sales.coef_[0] > 0 else 'Decreasing'
#         })

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


# # ─────────────────────────────────────────────
# # ROUTE 2 — /anomaly
# # ─────────────────────────────────────────────
# @app.route('/anomaly', methods=['POST'])
# def detect_anomaly():
#     try:
#         data     = request.json
#         invoices = data.get('invoices', [])

#         if len(invoices) < 3:
#             return jsonify({'anomalies': [], 'message': 'Need more invoices for anomaly detection'})

#         amounts = np.array([inv['amount'] for inv in invoices])
#         mean    = float(np.mean(amounts))
#         std     = float(np.std(amounts))
#         q1      = float(np.percentile(amounts, 25))
#         q3      = float(np.percentile(amounts, 75))
#         iqr     = q3 - q1

#         anomalies       = []
#         scored_invoices = []

#         for inv in invoices:
#             z_score   = abs(inv['amount'] - mean) / std if std > 0 else 0
#             iqr_score = abs(inv['amount'] - mean) / iqr if iqr > 0 else 0
#             raw_risk  = min(100, round((z_score * 25) + (iqr_score * 10), 1))
#             risk_level = (
#                 'Critical' if raw_risk >= 75 else
#                 'High'     if raw_risk >= 50 else
#                 'Medium'   if raw_risk >= 25 else
#                 'Low'
#             )
#             scored_invoices.append({
#                 'id':         inv['id'],
#                 'partyName':  inv['partyName'],
#                 'amount':     inv['amount'],
#                 'risk_score': raw_risk,
#                 'risk_level': risk_level,
#                 'z_score':    round(z_score, 2)
#             })
#             if z_score > 2:
#                 anomalies.append({
#                     'id':         inv['id'],
#                     'partyName':  inv['partyName'],
#                     'amount':     inv['amount'],
#                     'risk_score': raw_risk,
#                     'risk_level': risk_level,
#                     'reason':     f'Unusual amount (Rs.{inv["amount"]:,}) compared to average (Rs.{round(mean, 2):,})',
#                     'z_score':    round(z_score, 2)
#                 })

#         return jsonify({
#             'anomalies':           anomalies,
#             'all_invoices_scored': sorted(scored_invoices, key=lambda x: x['risk_score'], reverse=True),
#             'total_invoices':      len(invoices),
#             'average_amount':      round(mean, 2),
#             'std_deviation':       round(std, 2),
#             'statistics': {
#                 'mean': round(mean, 2),
#                 'std':  round(std,  2),
#                 'q1':   round(q1,   2),
#                 'q3':   round(q3,   2),
#                 'iqr':  round(iqr,  2)
#             }
#         })

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


# # ─────────────────────────────────────────────
# # ROUTE 3 — /graph  (Forecast + Confidence Band)
# # ─────────────────────────────────────────────
# @app.route('/graph', methods=['POST'])
# def generate_graph():
#     try:
#         data     = request.json
#         invoices = data.get('invoices', [])

#         X, y_sales, _, months = prepare_monthly_data(invoices)

#         if len(months) < 2:
#             return jsonify({'error': 'Need at least 2 months of sales data'}), 400

#         model     = LinearRegression().fit(X, y_sales)
#         y_pred    = model.predict(X)
#         next_X    = np.array([[len(months)]])
#         next_pred = max(0, model.predict(next_X)[0])

#         r2   = r2_score(y_sales, y_pred)
#         mae  = mean_absolute_error(y_sales, y_pred)
#         rmse = np.sqrt(mean_squared_error(y_sales, y_pred))

#         residuals = y_sales - y_pred
#         res_std   = np.std(residuals)
#         t_val     = stats.t.ppf(0.975, df=max(1, len(months) - 2))
#         ci        = t_val * res_std

#         X_plot  = np.arange(len(months) + 1).reshape(-1, 1)
#         y_plot  = model.predict(X_plot)
#         upper   = y_plot + ci
#         lower   = np.maximum(0, y_plot - ci)

#         fig, ax = plt.subplots(figsize=(10, 5.5))
#         fig.patch.set_facecolor(BG_FIG)
#         ax.set_facecolor(BG_AX)

#         month_labels = months + ['Next Month\n(Predicted)']
#         x_ticks      = np.arange(len(month_labels))

#         ax.fill_between(x_ticks, lower, upper,
#                         alpha=0.15, color=C_BLUE, label='95% Confidence Band')
#         ax.plot(x_ticks, y_plot, '--', color=C_BLUE,
#                 linewidth=1.8, label='Regression Line', zorder=3)
#         ax.plot(x_ticks[:len(months)], y_sales,
#                 'o-', color=C_GREEN, linewidth=2.5,
#                 markersize=8, label='Actual Sales', zorder=5)
#         ax.plot(x_ticks[:len(months)], y_pred,
#                 's', color=C_YELLOW, markersize=6,
#                 label='Model Fitted Values', zorder=4)
#         ax.plot(x_ticks[-1], next_pred,
#                 '*', color=C_ORANGE, markersize=16,
#                 label=f'Prediction: Rs.{next_pred:,.0f}', zorder=6)

#         ax.axvline(x=len(months) - 0.5, color=C_SPINE,
#                    linestyle=':', linewidth=1.2, alpha=0.8)
#         ax.text(len(months) - 0.44, ax.get_ylim()[1] * 0.95,
#                 'Forecast →', color=C_LABEL, fontsize=8)

#         metrics_text = (
#             f'R2 Score : {r2:.4f}\n'
#             f'MAE      : Rs.{mae:,.0f}\n'
#             f'RMSE     : Rs.{rmse:,.0f}'
#         )
#         ax.text(0.02, 0.97, metrics_text,
#                 transform=ax.transAxes, fontsize=9,
#                 verticalalignment='top',
#                 bbox=dict(boxstyle='round,pad=0.5',
#                           facecolor=C_BOX_BG, edgecolor=C_BOX_ED, alpha=0.95),
#                 color=C_TEXT, fontfamily='monospace')

#         ax.set_xticks(x_ticks)
#         ax.set_xticklabels(month_labels, color=C_TICK, fontsize=9)
#         ax.yaxis.set_major_formatter(
#             plt.FuncFormatter(lambda v, _: f'Rs.{v/1e5:.1f}L' if v >= 1e5 else f'Rs.{v:,.0f}')
#         )
#         ax.tick_params(colors=C_TICK)
#         ax.set_title('Sales Forecast — Predicted vs Actual with Confidence Interval',
#                      color=C_TITLE, fontsize=13, fontweight='bold', pad=14)
#         ax.set_xlabel('Month', color=C_LABEL, fontsize=10)
#         ax.set_ylabel('Sales', color=C_LABEL, fontsize=10)
#         ax.grid(True, linestyle='--', alpha=0.5, color=C_GRID)
#         ax.spines[:].set_color(C_SPINE)
#         ax.legend(facecolor=BG_FIG, edgecolor=C_SPINE,
#                   labelcolor=C_TEXT, fontsize=8.5,
#                   loc='upper left', bbox_to_anchor=(0.0, 0.78))

#         plt.tight_layout()

#         buf = io.BytesIO()
#         plt.savefig(buf, format='png', dpi=130,
#                     bbox_inches='tight', facecolor=BG_FIG)
#         buf.seek(0)
#         img_base64 = base64.b64encode(buf.read()).decode('utf-8')
#         plt.close()

#         return jsonify({
#             'graph': img_base64,
#             'metrics': {
#                 'r2_score': round(r2,   4),
#                 'mae':      round(mae,  2),
#                 'rmse':     round(rmse, 2)
#             },
#             'next_month_prediction': round(float(next_pred), 2),
#             'confidence_interval':   round(float(ci), 2)
#         })

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


# # ─────────────────────────────────────────────
# # ROUTE 4 — /model-comparison
# # ─────────────────────────────────────────────
# @app.route('/model-comparison', methods=['POST'])
# def model_comparison():
#     try:
#         data     = request.json
#         invoices = data.get('invoices', [])

#         X, y_sales, _, months = prepare_monthly_data(invoices)

#         if len(months) < 2:
#             return jsonify({'error': 'Need at least 2 months of data'}), 400

#         lr_model   = LinearRegression().fit(X, y_sales)
#         poly_model = make_pipeline(
#             PolynomialFeatures(degree=2), LinearRegression()
#         ).fit(X, y_sales)

#         lr_pred   = lr_model.predict(X)
#         poly_pred = poly_model.predict(X)

#         lr_r2     = r2_score(y_sales, lr_pred)
#         poly_r2   = r2_score(y_sales, poly_pred)
#         lr_rmse   = np.sqrt(mean_squared_error(y_sales, lr_pred))
#         poly_rmse = np.sqrt(mean_squared_error(y_sales, poly_pred))

#         next_X    = np.array([[len(months)]])
#         lr_next   = max(0, lr_model.predict(next_X)[0])
#         poly_next = max(0, poly_model.predict(next_X)[0])

#         winner       = 'Linear Regression' if lr_r2 >= poly_r2 else 'Polynomial Regression'
#         winner_color = C_BLUE if lr_r2 >= poly_r2 else C_ORANGE

#         fig, ax = plt.subplots(figsize=(10, 5.5))
#         fig.patch.set_facecolor(BG_FIG)
#         ax.set_facecolor(BG_AX)

#         x_ticks = np.arange(len(months))

#         ax.plot(x_ticks, y_sales, 'o-', color=C_GREEN,
#                 linewidth=2.5, markersize=9, label='Actual Sales', zorder=5)
#         ax.plot(x_ticks, lr_pred, '--', color=C_BLUE,
#                 linewidth=2, label=f'Linear Regression  (R2={lr_r2:.3f})', zorder=4)
#         ax.plot(x_ticks, poly_pred, '--', color=C_ORANGE,
#                 linewidth=2, label=f'Polynomial Degree-2 (R2={poly_r2:.3f})', zorder=4)

#         comparison_text = (
#             f'Linear     -> R2={lr_r2:.3f}  RMSE=Rs.{lr_rmse:,.0f}\n'
#             f'Polynomial -> R2={poly_r2:.3f}  RMSE=Rs.{poly_rmse:,.0f}\n'
#             f'Best Model -> {winner}'
#         )
#         ax.text(0.02, 0.97, comparison_text,
#                 transform=ax.transAxes, fontsize=9,
#                 verticalalignment='top',
#                 bbox=dict(boxstyle='round,pad=0.5',
#                           facecolor=C_BOX_BG, edgecolor=winner_color, alpha=0.95),
#                 color=C_TEXT, fontfamily='monospace')

#         ax.set_xticks(x_ticks)
#         ax.set_xticklabels(months, color=C_TICK, fontsize=9)
#         ax.yaxis.set_major_formatter(
#             plt.FuncFormatter(lambda v, _: f'Rs.{v/1e5:.1f}L' if v >= 1e5 else f'Rs.{v:,.0f}')
#         )
#         ax.tick_params(colors=C_TICK)
#         ax.set_title(f'Model Comparison — Winner: {winner}',
#                      color=C_TITLE, fontsize=13, fontweight='bold', pad=14)
#         ax.set_xlabel('Month', color=C_LABEL, fontsize=10)
#         ax.set_ylabel('Sales', color=C_LABEL, fontsize=10)
#         ax.grid(True, linestyle='--', alpha=0.5, color=C_GRID)
#         ax.spines[:].set_color(C_SPINE)
#         ax.legend(facecolor=BG_FIG, edgecolor=C_SPINE,
#                   labelcolor=C_TEXT, fontsize=9)

#         plt.tight_layout()

#         buf = io.BytesIO()
#         plt.savefig(buf, format='png', dpi=130,
#                     bbox_inches='tight', facecolor=BG_FIG)
#         buf.seek(0)
#         img_base64 = base64.b64encode(buf.read()).decode('utf-8')
#         plt.close()

#         return jsonify({
#             'graph':  img_base64,
#             'winner': winner,
#             'models': {
#                 'linear':     {'r2': round(lr_r2,   4), 'rmse': round(lr_rmse,   2), 'next_prediction': round(float(lr_next),   2)},
#                 'polynomial': {'r2': round(poly_r2, 4), 'rmse': round(poly_rmse, 2), 'next_prediction': round(float(poly_next), 2)}
#             }
#         })

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


# # ─────────────────────────────────────────────
# # ROUTE 5 — /insights
# # ─────────────────────────────────────────────
# @app.route('/insights', methods=['POST'])
# def business_insights():
#     try:
#         data     = request.json
#         invoices = data.get('invoices', [])

#         X, y_sales, y_gst, months = prepare_monthly_data(invoices)

#         if len(months) < 2:
#             return jsonify({'error': 'Need at least 2 months of data'}), 400

#         mom_growth = []
#         for i in range(1, len(y_sales)):
#             if y_sales[i - 1] != 0:
#                 growth = ((y_sales[i] - y_sales[i - 1]) / y_sales[i - 1]) * 100
#                 mom_growth.append(round(growth, 2))

#         avg_growth     = round(float(np.mean(mom_growth)), 2) if mom_growth else 0
#         peak_month     = months[int(np.argmax(y_sales))]
#         peak_sales     = float(np.max(y_sales))
#         gst_ratio      = round(float(np.mean(y_gst / y_sales * 100)), 2) if y_sales.sum() > 0 else 0
#         gst_model      = LinearRegression().fit(X, y_gst)
#         gst_trend      = 'Increasing' if gst_model.coef_[0] > 0 else 'Decreasing'

#         Xp, y_purchase, _, _ = prepare_monthly_data(invoices, 'PURCHASE')
#         purchase_ratio = round(float(y_purchase.sum() / y_sales.sum() * 100), 2) if y_sales.sum() > 0 else 0

#         fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
#         fig.patch.set_facecolor(BG_FIG)

#         x_ticks = np.arange(len(months))

#         # Left — Sales bar + trend line
#         ax1.set_facecolor(BG_AX)
#         ax1.bar(x_ticks, y_sales, color=C_BLUE, alpha=0.80, label='Monthly Sales')
#         ax1.plot(x_ticks, LinearRegression().fit(X, y_sales).predict(X),
#                  '--', color=C_GREEN, linewidth=2.2, label='Trend Line')
#         ax1.set_title('Monthly Sales Trend', color=C_TITLE, fontsize=11, fontweight='bold')
#         ax1.set_xticks(x_ticks)
#         ax1.set_xticklabels(months, color=C_TICK, fontsize=8, rotation=15)
#         ax1.yaxis.set_major_formatter(
#             plt.FuncFormatter(lambda v, _: f'Rs.{v/1e5:.1f}L' if v >= 1e5 else f'Rs.{v:,.0f}')
#         )
#         ax1.tick_params(colors=C_TICK)
#         ax1.grid(True, linestyle='--', alpha=0.5, color=C_GRID)
#         ax1.spines[:].set_color(C_SPINE)
#         ax1.legend(facecolor=BG_FIG, edgecolor=C_SPINE, labelcolor=C_TEXT, fontsize=8)

#         # Right — GST bar
#         ax2.set_facecolor(BG_AX)
#         ax2.bar(x_ticks, y_gst, color=C_AMBER, alpha=0.80, label='GST Collected')
#         ax2.set_title('Monthly GST Collection Trend', color=C_TITLE, fontsize=11, fontweight='bold')
#         ax2.set_xticks(x_ticks)
#         ax2.set_xticklabels(months, color=C_TICK, fontsize=8, rotation=15)
#         ax2.yaxis.set_major_formatter(
#             plt.FuncFormatter(lambda v, _: f'Rs.{v/1e5:.1f}L' if v >= 1e5 else f'Rs.{v:,.0f}')
#         )
#         ax2.tick_params(colors=C_TICK)
#         ax2.grid(True, linestyle='--', alpha=0.5, color=C_GRID)
#         ax2.spines[:].set_color(C_SPINE)
#         ax2.legend(facecolor=BG_FIG, edgecolor=C_SPINE, labelcolor=C_TEXT, fontsize=8)

#         plt.suptitle('Business Intelligence Dashboard',
#                      color=C_TITLE, fontsize=13, fontweight='bold', y=1.01)
#         plt.tight_layout()

#         buf = io.BytesIO()
#         plt.savefig(buf, format='png', dpi=130,
#                     bbox_inches='tight', facecolor=BG_FIG)
#         buf.seek(0)
#         img_base64 = base64.b64encode(buf.read()).decode('utf-8')
#         plt.close()

#         return jsonify({
#             'graph': img_base64,
#             'insights': {
#                 'average_monthly_growth_percent':  avg_growth,
#                 'peak_sales_month':                peak_month,
#                 'peak_sales_amount':               round(peak_sales, 2),
#                 'effective_gst_rate_percent':      gst_ratio,
#                 'gst_collection_trend':            gst_trend,
#                 'purchase_to_sales_ratio_percent': purchase_ratio,
#                 'mom_growth_rates':                mom_growth,
#                 'total_months_analyzed':           len(months)
#             }
#         })

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


# # ─────────────────────────────────────────────
# # ROUTE 6 — /anomaly-graph
# # ─────────────────────────────────────────────
# @app.route('/anomaly-graph', methods=['POST'])
# def anomaly_graph():
#     try:
#         data     = request.json
#         invoices = data.get('invoices', [])

#         if len(invoices) < 3:
#             return jsonify({'error': 'Need at least 3 invoices'}), 400

#         amounts = np.array([inv['amount'] for inv in invoices])
#         mean    = np.mean(amounts)
#         std     = np.std(amounts)
#         iqr     = np.percentile(amounts, 75) - np.percentile(amounts, 25)

#         names, scores, colors_bar = [], [], []
#         for inv in invoices:
#             z     = abs(inv['amount'] - mean) / std if std > 0 else 0
#             iq    = abs(inv['amount'] - mean) / iqr if iqr > 0 else 0
#             score = min(100, round((z * 25) + (iq * 10), 1))
#             names.append(inv['partyName'][:14])
#             scores.append(score)
#             colors_bar.append(
#                 C_RED    if score >= 75 else
#                 C_ORANGE if score >= 50 else
#                 C_YELLOW if score >= 25 else
#                 C_GREEN
#             )

#         fig, ax = plt.subplots(figsize=(10, max(4, len(names) * 0.6)))
#         fig.patch.set_facecolor(BG_FIG)
#         ax.set_facecolor(BG_AX)

#         bars = ax.barh(names, scores, color=colors_bar, alpha=0.88, height=0.55)

#         for bar, score in zip(bars, scores):
#             ax.text(bar.get_width() + 1,
#                     bar.get_y() + bar.get_height() / 2,
#                     f'{score}', va='center', ha='left',
#                     color=C_TEXT, fontsize=9, fontweight='bold')

#         ax.axvline(75, color=C_RED,    linestyle='--', linewidth=1.2, alpha=0.7)
#         ax.axvline(50, color=C_ORANGE, linestyle='--', linewidth=1.2, alpha=0.7)
#         ax.axvline(25, color=C_YELLOW, linestyle='--', linewidth=1.2, alpha=0.7)

#         legend_items = [
#             mpatches.Patch(color=C_RED,    label='Critical  >= 75'),
#             mpatches.Patch(color=C_ORANGE, label='High      >= 50'),
#             mpatches.Patch(color=C_YELLOW, label='Medium    >= 25'),
#             mpatches.Patch(color=C_GREEN,  label='Low        < 25'),
#         ]
#         ax.legend(handles=legend_items, facecolor=BG_FIG,
#                   edgecolor=C_SPINE, labelcolor=C_TEXT, fontsize=8.5)

#         ax.set_xlim(0, 115)
#         ax.set_xlabel('Risk Score  (0 = Safe   100 = Critical)',
#                       color=C_LABEL, fontsize=10)
#         ax.set_title('Invoice Risk Scoring — Anomaly Detection',
#                      color=C_TITLE, fontsize=13, fontweight='bold', pad=12)
#         ax.tick_params(colors=C_TICK)
#         ax.grid(True, axis='x', linestyle='--', alpha=0.5, color=C_GRID)
#         ax.spines[:].set_color(C_SPINE)

#         plt.tight_layout()

#         buf = io.BytesIO()
#         plt.savefig(buf, format='png', dpi=130,
#                     bbox_inches='tight', facecolor=BG_FIG)
#         buf.seek(0)
#         img_base64 = base64.b64encode(buf.read()).decode('utf-8')
#         plt.close()

#         return jsonify({'graph': img_base64})

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


# if __name__ == '__main__':
#     app.run(port=5001, debug=True, host='0.0.0.0')














































from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import io
import base64
from scipy import stats

app = Flask(__name__)
CORS(app)

# ══════════════════════════════════════════════════════
#  PROFESSIONAL BUSINESS COLOUR PALETTE
#  Inspired by CA / Finance report aesthetics
# ══════════════════════════════════════════════════════
PRIMARY    = '#1B3A6B'   # Deep navy  – main bars / lines
SECONDARY  = '#2E86AB'   # Steel blue – secondary series
ACCENT     = '#F4A261'   # Amber      – GST / highlights
SUCCESS    = '#2A9D8F'   # Teal green – positive trend
DANGER     = '#E63946'   # Red        – anomaly / critical
WARNING    = '#E9C46A'   # Soft gold  – medium risk
NEUTRAL    = '#6C757D'   # Grey       – gridlines, spines

BG_FIG     = '#FFFFFF'
BG_AX      = '#FAFBFC'
C_TITLE    = '#0D1B2A'
C_LABEL    = '#374151'
C_TICK     = '#4B5563'
C_GRID     = '#E5E7EB'
C_SPINE    = '#9CA3AF'

# Monochrome-safe hatches for PPT printing
HATCH_SALE = ''
HATCH_GST  = '//'

FONT_TITLE  = {'fontsize': 13, 'fontweight': 'bold', 'color': C_TITLE, 'pad': 14}
FONT_LABEL  = {'fontsize': 10, 'color': C_LABEL}
FONT_TICK   = {'labelcolor': C_TICK, 'labelsize': 9}


def inr_fmt(v, _=None):
    """Format y-axis values as Indian Rupee shorthand."""
    if v >= 1e7:
        return f'₹{v/1e7:.1f}Cr'
    if v >= 1e5:
        return f'₹{v/1e5:.1f}L'
    if v >= 1e3:
        return f'₹{v/1e3:.0f}K'
    return f'₹{v:,.0f}'


def buf_to_b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor=BG_FIG)
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return b64


def prepare_monthly_data(invoices, invoice_type='SALE'):
    sales_by_month = {}
    gst_by_month   = {}
    for inv in invoices:
        if inv['type'] == invoice_type:
            date = inv['date'][:7]
            sales_by_month[date] = sales_by_month.get(date, 0) + inv['amount']
            gst_by_month[date]   = gst_by_month.get(date, 0)   + inv['gstAmount']
    months  = sorted(sales_by_month.keys())
    y_sales = np.array([sales_by_month[m] for m in months])
    y_gst   = np.array([gst_by_month[m]   for m in months])
    X       = np.arange(len(months)).reshape(-1, 1)
    return X, y_sales, y_gst, months


def apply_base_style(ax, fig):
    fig.patch.set_facecolor(BG_FIG)
    ax.set_facecolor(BG_AX)
    ax.grid(True, axis='y', linestyle='--', linewidth=0.6, color=C_GRID, alpha=0.9)
    ax.grid(False, axis='x')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(C_SPINE)
    ax.spines['bottom'].set_color(C_SPINE)
    ax.tick_params(**FONT_TICK)


def watermark(fig, text='GST Business Tracker'):
    fig.text(0.99, 0.01, text, ha='right', va='bottom',
             fontsize=7.5, color='#CCCCCC', style='italic')


# ══════════════════════════════════════════════════════
# ROUTE 1  /predict
# ══════════════════════════════════════════════════════
@app.route('/predict', methods=['POST'])
def predict_gst():
    try:
        data     = request.json
        invoices = data.get('invoices', [])

        if len(invoices) < 2:
            return jsonify({
                'predicted_sales': 0,
                'predicted_gst':   0,
                'message':         'Add more invoices to enable prediction.'
            })

        X, y_sales, y_gst, months = prepare_monthly_data(invoices)

        if len(months) < 2:
            return jsonify({
                'predicted_sales': round(float(y_sales.sum()) * 1.1, 2),
                'predicted_gst':   round(float(y_gst.sum())   * 1.1, 2),
                'message':         'Estimated based on available data'
            })

        model_sales = LinearRegression().fit(X, y_sales)
        model_gst   = LinearRegression().fit(X, y_gst)

        next_X          = np.array([[len(months)]])
        predicted_sales = max(0, float(model_sales.predict(next_X)[0]))
        predicted_gst   = max(0, float(model_gst.predict(next_X)[0]))

        y_sales_pred = model_sales.predict(X)
        r2   = round(float(r2_score(y_sales, y_sales_pred)), 4)
        mae  = round(float(mean_absolute_error(y_sales, y_sales_pred)), 2)
        rmse = round(float(np.sqrt(mean_squared_error(y_sales, y_sales_pred))), 2)

        growth_rate = 0
        if len(y_sales) >= 2 and y_sales[-2] != 0:
            growth_rate = round(((y_sales[-1] - y_sales[-2]) / y_sales[-2]) * 100, 2)

        interpretation = (
            'High confidence' if r2 > 0.8 else
            'Moderate confidence' if r2 > 0.5 else
            'Needs more months for higher accuracy'
        )

        return jsonify({
            'predicted_sales':       round(predicted_sales, 2),
            'predicted_gst':         round(predicted_gst, 2),
            'months_analyzed':       len(months),
            'message':               f'Based on {len(months)} months of data',
            'model_accuracy': {
                'r2_score':          r2,
                'mae':               mae,
                'rmse':              rmse,
                'interpretation':    interpretation
            },
            'growth_rate_percent':   growth_rate,
            'trend':                 'Increasing' if model_sales.coef_[0] > 0 else 'Decreasing'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ══════════════════════════════════════════════════════
# ROUTE 2  /anomaly
# ══════════════════════════════════════════════════════
@app.route('/anomaly', methods=['POST'])
def detect_anomaly():
    try:
        data     = request.json
        invoices = data.get('invoices', [])

        if len(invoices) < 3:
            return jsonify({'anomalies': [], 'message': 'Need at least 3 invoices for anomaly detection'})

        amounts = np.array([inv['amount'] for inv in invoices])
        mean    = float(np.mean(amounts))
        std     = float(np.std(amounts))
        q1      = float(np.percentile(amounts, 25))
        q3      = float(np.percentile(amounts, 75))
        iqr     = q3 - q1

        anomalies       = []
        scored_invoices = []

        for inv in invoices:
            z_score   = abs(inv['amount'] - mean) / std if std > 0 else 0
            iqr_score = abs(inv['amount'] - mean) / iqr if iqr > 0 else 0
            raw_risk  = min(100, round((z_score * 25) + (iqr_score * 10), 1))
            risk_level = (
                'Critical' if raw_risk >= 75 else
                'High'     if raw_risk >= 50 else
                'Medium'   if raw_risk >= 25 else
                'Low'
            )
            scored_invoices.append({
                'id':         inv['id'],
                'partyName':  inv['partyName'],
                'amount':     inv['amount'],
                'risk_score': raw_risk,
                'risk_level': risk_level,
                'z_score':    round(z_score, 2)
            })
            if z_score > 2:
                anomalies.append({
                    'id':         inv['id'],
                    'partyName':  inv['partyName'],
                    'amount':     inv['amount'],
                    'risk_score': raw_risk,
                    'risk_level': risk_level,
                    'reason':     f'Invoice amount ₹{inv["amount"]:,} deviates significantly from average ₹{round(mean, 2):,}',
                    'z_score':    round(z_score, 2)
                })

        return jsonify({
            'anomalies':           anomalies,
            'all_invoices_scored': sorted(scored_invoices, key=lambda x: x['risk_score'], reverse=True),
            'total_invoices':      len(invoices),
            'average_amount':      round(mean, 2),
            'std_deviation':       round(std, 2),
            'statistics': {
                'mean': round(mean, 2),
                'std':  round(std,  2),
                'q1':   round(q1,   2),
                'q3':   round(q3,   2),
                'iqr':  round(iqr,  2)
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ══════════════════════════════════════════════════════
# ROUTE 3  /graph  — Sales vs GST Grouped Bar Chart
#   Professional business chart — no regression clutter
# ══════════════════════════════════════════════════════
@app.route('/graph', methods=['POST'])
def generate_graph():
    try:
        data     = request.json
        invoices = data.get('invoices', [])

        X, y_sales, y_gst, months = prepare_monthly_data(invoices)

        if len(months) < 1:
            return jsonify({'error': 'No sales data found'}), 400

        # ── Forecast for next month (only shown if ≥ 2 months) ──
        has_forecast  = len(months) >= 2
        next_pred     = None
        next_gst_pred = None
        r2 = mae = rmse = ci = None

        if has_forecast:
            model_s = LinearRegression().fit(X, y_sales)
            model_g = LinearRegression().fit(X, y_gst)
            nX            = np.array([[len(months)]])
            next_pred     = max(0, float(model_s.predict(nX)[0]))
            next_gst_pred = max(0, float(model_g.predict(nX)[0]))
            y_pred = model_s.predict(X)
            r2   = round(float(r2_score(y_sales, y_pred)), 4)
            mae  = round(float(mean_absolute_error(y_sales, y_pred)), 2)
            rmse = round(float(np.sqrt(mean_squared_error(y_sales, y_pred))), 2)
            res_std = np.std(y_sales - y_pred)
            t_val   = stats.t.ppf(0.975, df=max(1, len(months) - 2))
            ci      = round(float(t_val * res_std), 2)

        # ── Build chart data ──
        display_months = months[:]
        display_sales  = list(y_sales)
        display_gst    = list(y_gst)

        if has_forecast:
            # Format next-month label nicely
            last_yr, last_mo = int(months[-1][:4]), int(months[-1][5:])
            next_mo = last_mo + 1 if last_mo < 12 else 1
            next_yr = last_yr if last_mo < 12 else last_yr + 1
            display_months.append(f'{next_yr}-{next_mo:02d}\n(Forecast)')
            display_sales.append(next_pred)
            display_gst.append(next_gst_pred)

        n      = len(display_months)
        x      = np.arange(n)
        width  = 0.38
        fig_w  = max(9, n * 1.3)
        fig, ax = plt.subplots(figsize=(fig_w, 5.5))
        apply_base_style(ax, fig)

        # ── Bars ──
        bars_s = ax.bar(x - width / 2, display_sales, width,
                        label='Net Sales', color=PRIMARY, alpha=0.88,
                        edgecolor='white', linewidth=0.6, zorder=3)
        bars_g = ax.bar(x + width / 2, display_gst, width,
                        label='GST Collected', color=ACCENT, alpha=0.88,
                        edgecolor='white', linewidth=0.6, zorder=3)

        # Shade forecast columns differently
        if has_forecast:
            ax.bar(n - 1 - width / 2, display_sales[-1], width,
                   color=SECONDARY, alpha=0.65, edgecolor=PRIMARY,
                   linewidth=1.0, linestyle='--', zorder=4,
                   label='_nolegend_')
            ax.bar(n - 1 + width / 2, display_gst[-1], width,
                   color='#F4A261', alpha=0.55, edgecolor=ACCENT,
                   linewidth=1.0, linestyle='--', zorder=4,
                   label='_nolegend_')
            # Vertical separator before forecast
            ax.axvline(x=n - 1.5, color=C_SPINE, linestyle=':', linewidth=1.2, alpha=0.7)
            ax.text(n - 1.5 + 0.04, ax.get_ylim()[1] * 0.97,
                    'Forecast →', color=C_LABEL, fontsize=8, va='top')

        # ── Value labels on bars ──
        def label_bars(bars, vals):
            for bar, val in zip(bars, vals):
                h = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2, h + max(vals) * 0.012,
                        inr_fmt(val), ha='center', va='bottom',
                        fontsize=7.5, color=C_TITLE, fontweight='semibold')

        label_bars(bars_s, display_sales)
        label_bars(bars_g, display_gst)

        # ── Axes ──
        ax.set_xticks(x)
        ax.set_xticklabels(display_months, **FONT_TICK)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(inr_fmt))
        ax.set_xlabel('Month', **FONT_LABEL)
        ax.set_ylabel('Amount (₹)', **FONT_LABEL)
        ax.set_title('Monthly Sales & GST Collection', **FONT_TITLE)
        ax.set_ylim(0, max(display_sales + display_gst) * 1.20)

        # ── Legend ──
        legend_handles = [
            mpatches.Patch(color=PRIMARY, alpha=0.88, label='Net Sales'),
            mpatches.Patch(color=ACCENT,  alpha=0.88, label='GST Collected'),
        ]
        if has_forecast:
            legend_handles.append(
                mpatches.Patch(color=SECONDARY, alpha=0.65,
                               label='Forecast (Next Month)', linestyle='--')
            )
        ax.legend(handles=legend_handles, frameon=True,
                  facecolor=BG_FIG, edgecolor=C_SPINE,
                  fontsize=9, loc='upper left')

        watermark(fig)
        plt.tight_layout()

        return jsonify({
            'graph':                 buf_to_b64(fig),
            'metrics': {
                'r2_score': r2,
                'mae':      mae,
                'rmse':     rmse
            } if has_forecast else {},
            'next_month_prediction': round(next_pred, 2)   if next_pred     else None,
            'next_gst_prediction':   round(next_gst_pred, 2) if next_gst_pred else None,
            'confidence_interval':   ci
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ══════════════════════════════════════════════════════
# ROUTE 4  /model-comparison  — Side-by-side model metrics
#   Shown as a clean bar metric chart — no messy overlaid lines
# ══════════════════════════════════════════════════════
@app.route('/model-comparison', methods=['POST'])
def model_comparison():
    try:
        data     = request.json
        invoices = data.get('invoices', [])

        X, y_sales, _, months = prepare_monthly_data(invoices)

        if len(months) < 2:
            return jsonify({'error': 'Need at least 2 months of data'}), 400

        lr_model   = LinearRegression().fit(X, y_sales)
        poly_model = make_pipeline(
            PolynomialFeatures(degree=2), LinearRegression()
        ).fit(X, y_sales)

        lr_pred   = lr_model.predict(X)
        poly_pred = poly_model.predict(X)

        lr_r2     = r2_score(y_sales, lr_pred)
        poly_r2   = r2_score(y_sales, poly_pred)
        lr_rmse   = np.sqrt(mean_squared_error(y_sales, lr_pred))
        poly_rmse = np.sqrt(mean_squared_error(y_sales, poly_pred))
        lr_mae    = mean_absolute_error(y_sales, lr_pred)
        poly_mae  = mean_absolute_error(y_sales, poly_pred)

        next_X    = np.array([[len(months)]])
        lr_next   = max(0, float(lr_model.predict(next_X)[0]))
        poly_next = max(0, float(poly_model.predict(next_X)[0]))

        winner = 'Linear Regression' if lr_r2 >= poly_r2 else 'Polynomial Regression'

        # ── Figure: 1×3 metric bar charts ──
        fig, axes = plt.subplots(1, 3, figsize=(12, 5))
        fig.patch.set_facecolor(BG_FIG)

        metrics = [
            ('R² Score\n(Higher is better)', [lr_r2, poly_r2], True,   1.0),
            ('MAE — Mean Abs Error\n(Lower is better)',  [lr_mae, poly_mae],  False, None),
            ('RMSE\n(Lower is better)',       [lr_rmse, poly_rmse], False, None),
        ]
        labels = ['Linear\nRegression', 'Polynomial\nDegree-2']

        for ax, (title, vals, higher_better, max_val) in zip(axes, metrics):
            apply_base_style(ax, fig)
            best_idx = int(np.argmax(vals) if higher_better else np.argmin(vals))
            colors   = [PRIMARY if i == best_idx else SECONDARY for i in range(2)]

            bars = ax.bar(labels, vals, color=colors, alpha=0.88,
                          edgecolor='white', linewidth=0.8, width=0.45)

            for bar, val in zip(bars, vals):
                fmt = f'{val:.4f}' if max_val else inr_fmt(val)
                ax.text(bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + (max(vals) * 0.03 if max(vals) > 0 else 0.02),
                        fmt, ha='center', va='bottom',
                        fontsize=9, fontweight='bold', color=C_TITLE)

            if max_val:
                ax.set_ylim(0, max_val * 1.25)
            else:
                ax.set_ylim(0, max(vals) * 1.30 if max(vals) > 0 else 1)

            ax.set_title(title, fontsize=9.5, fontweight='bold',
                         color=C_TITLE, pad=10)
            ax.yaxis.set_major_formatter(
                mticker.FuncFormatter(lambda v, _: f'{v:.3f}') if max_val
                else mticker.FuncFormatter(inr_fmt)
            )
            ax.tick_params(**FONT_TICK)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color(C_SPINE)
            ax.spines['bottom'].set_color(C_SPINE)

            # Star the winner bar
            winner_bar = bars[best_idx]
            ax.text(winner_bar.get_x() + winner_bar.get_width() / 2,
                    winner_bar.get_height() + max(vals) * (0.10 if max_val else 0.12),
                    '★ Best', ha='center', fontsize=8,
                    color=SUCCESS, fontweight='bold')

        fig.suptitle(f'Model Performance Comparison  ·  Recommended: {winner}',
                     fontsize=12, fontweight='bold', color=C_TITLE, y=1.02)

        watermark(fig)
        plt.tight_layout()

        return jsonify({
            'graph':  buf_to_b64(fig),
            'winner': winner,
            'models': {
                'linear':     {'r2': round(lr_r2,   4), 'rmse': round(lr_rmse,   2),
                               'mae': round(lr_mae,  2), 'next_prediction': round(lr_next,   2)},
                'polynomial': {'r2': round(poly_r2, 4), 'rmse': round(poly_rmse, 2),
                               'mae': round(poly_mae, 2), 'next_prediction': round(poly_next, 2)}
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ══════════════════════════════════════════════════════
# ROUTE 5  /insights  — Business Intelligence Dashboard
# ══════════════════════════════════════════════════════
@app.route('/insights', methods=['POST'])
def business_insights():
    try:
        data     = request.json
        invoices = data.get('invoices', [])

        X, y_sales, y_gst, months = prepare_monthly_data(invoices)

        if len(months) < 2:
            return jsonify({'error': 'Need at least 2 months of data'}), 400

        mom_growth = []
        for i in range(1, len(y_sales)):
            if y_sales[i - 1] != 0:
                growth = ((y_sales[i] - y_sales[i - 1]) / y_sales[i - 1]) * 100
                mom_growth.append(round(growth, 2))

        avg_growth  = round(float(np.mean(mom_growth)), 2) if mom_growth else 0
        peak_month  = months[int(np.argmax(y_sales))]
        peak_sales  = float(np.max(y_sales))
        gst_ratio   = round(float(np.mean(y_gst / y_sales * 100)), 2) if y_sales.sum() > 0 else 0
        gst_model   = LinearRegression().fit(X, y_gst)
        gst_trend   = 'Increasing' if gst_model.coef_[0] > 0 else 'Decreasing'

        Xp, y_purchase, _, _ = prepare_monthly_data(invoices, 'PURCHASE')
        purchase_ratio = round(float(y_purchase.sum() / y_sales.sum() * 100), 2) if y_sales.sum() > 0 else 0

        x_ticks = np.arange(len(months))
        trend_line = LinearRegression().fit(X, y_sales).predict(X)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))
        fig.patch.set_facecolor(BG_FIG)

        # ── Left: Sales Bar + Trend ──
        apply_base_style(ax1, fig)
        ax1.bar(x_ticks, y_sales, color=PRIMARY, alpha=0.85,
                edgecolor='white', linewidth=0.6, label='Monthly Sales', zorder=3)
        ax1.plot(x_ticks, trend_line, color=SUCCESS, linewidth=2.2,
                 linestyle='--', marker='o', markersize=5,
                 label='Trend Line', zorder=4)

        for xi, val in zip(x_ticks, y_sales):
            ax1.text(xi, val + max(y_sales) * 0.015, inr_fmt(val),
                     ha='center', fontsize=7.5, color=C_TITLE, fontweight='semibold')

        ax1.set_xticks(x_ticks)
        ax1.set_xticklabels(months, fontsize=8.5, rotation=20, color=C_TICK, ha='right')
        ax1.yaxis.set_major_formatter(mticker.FuncFormatter(inr_fmt))
        ax1.set_title('Monthly Net Sales', **FONT_TITLE)
        ax1.set_ylabel('Sales Amount (₹)', **FONT_LABEL)
        ax1.set_ylim(0, max(y_sales) * 1.22)
        ax1.legend(fontsize=9, facecolor=BG_FIG, edgecolor=C_SPINE, frameon=True)

        # ── Right: GST Collection ──
        apply_base_style(ax2, fig)
        ax2.bar(x_ticks, y_gst, color=ACCENT, alpha=0.85,
                edgecolor='white', linewidth=0.6, label='GST Collected', zorder=3)

        gst_trend_line = LinearRegression().fit(X, y_gst).predict(X)
        ax2.plot(x_ticks, gst_trend_line, color=DANGER, linewidth=2.0,
                 linestyle='--', marker='o', markersize=5,
                 label='GST Trend', zorder=4)

        for xi, val in zip(x_ticks, y_gst):
            ax2.text(xi, val + max(y_gst) * 0.015, inr_fmt(val),
                     ha='center', fontsize=7.5, color=C_TITLE, fontweight='semibold')

        ax2.set_xticks(x_ticks)
        ax2.set_xticklabels(months, fontsize=8.5, rotation=20, color=C_TICK, ha='right')
        ax2.yaxis.set_major_formatter(mticker.FuncFormatter(inr_fmt))
        ax2.set_title('Monthly GST Collection', **FONT_TITLE)
        ax2.set_ylabel('GST Amount (₹)', **FONT_LABEL)
        ax2.set_ylim(0, max(y_gst) * 1.22)
        ax2.legend(fontsize=9, facecolor=BG_FIG, edgecolor=C_SPINE, frameon=True)

        fig.suptitle('Business Intelligence — Sales & GST Overview',
                     fontsize=13, fontweight='bold', color=C_TITLE, y=1.02)
        watermark(fig)
        plt.tight_layout()

        return jsonify({
            'graph': buf_to_b64(fig),
            'insights': {
                'average_monthly_growth_percent':  avg_growth,
                'peak_sales_month':                peak_month,
                'peak_sales_amount':               round(peak_sales, 2),
                'effective_gst_rate_percent':      gst_ratio,
                'gst_collection_trend':            gst_trend,
                'purchase_to_sales_ratio_percent': purchase_ratio,
                'mom_growth_rates':                mom_growth,
                'total_months_analyzed':           len(months)
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ══════════════════════════════════════════════════════
# ROUTE 6  /anomaly-graph  — Horizontal Risk Bar Chart
# ══════════════════════════════════════════════════════
@app.route('/anomaly-graph', methods=['POST'])
def anomaly_graph():
    try:
        data     = request.json
        invoices = data.get('invoices', [])

        if len(invoices) < 3:
            return jsonify({'error': 'Need at least 3 invoices'}), 400

        amounts = np.array([inv['amount'] for inv in invoices])
        mean    = np.mean(amounts)
        std     = np.std(amounts)
        iqr_val = np.percentile(amounts, 75) - np.percentile(amounts, 25)

        records = []
        for inv in invoices:
            z     = abs(inv['amount'] - mean) / std    if std    > 0 else 0
            iqr_s = abs(inv['amount'] - mean) / iqr_val if iqr_val > 0 else 0
            score = min(100, round((z * 25) + (iqr_s * 10), 1))
            risk_level = (
                'Critical' if score >= 75 else
                'High'     if score >= 50 else
                'Medium'   if score >= 25 else
                'Low'
            )
            records.append({
                'name':  inv['partyName'][:18],
                'score': score,
                'risk':  risk_level,
                'amount': inv['amount']
            })

        records.sort(key=lambda r: r['score'], reverse=True)

        RISK_COLORS = {
            'Critical': DANGER,
            'High':     '#E67E22',
            'Medium':   WARNING,
            'Low':      SUCCESS
        }

        names  = [r['name']  for r in records]
        scores = [r['score'] for r in records]
        colors = [RISK_COLORS[r['risk']] for r in records]

        fig_h  = max(4.5, len(names) * 0.55 + 1.5)
        fig, ax = plt.subplots(figsize=(10, fig_h))
        apply_base_style(ax, fig)
        ax.grid(True, axis='x', linestyle='--', linewidth=0.6, color=C_GRID)
        ax.grid(False, axis='y')

        bars = ax.barh(names, scores, color=colors, alpha=0.88,
                       height=0.52, edgecolor='white', linewidth=0.6, zorder=3)

        # Score labels
        for bar, rec in zip(bars, records):
            w = bar.get_width()
            ax.text(min(w + 1.5, 103), bar.get_y() + bar.get_height() / 2,
                    f'{rec["score"]}  |  {inr_fmt(rec["amount"])}',
                    va='center', ha='left', fontsize=8,
                    color=C_TITLE, fontweight='semibold')

        # Threshold lines
        for thresh, color, lbl in [(75, DANGER, 'Critical'), (50, '#E67E22', 'High'), (25, WARNING, 'Medium')]:
            ax.axvline(thresh, color=color, linestyle='--', linewidth=1.1, alpha=0.55, zorder=2)
            ax.text(thresh + 0.5, -0.6, lbl, color=color, fontsize=7.5, va='top', alpha=0.8)

        ax.set_xlim(0, 118)
        ax.set_xlabel('Risk Score  (0 = Low  ·  100 = Critical)', **FONT_LABEL)
        ax.set_title('Invoice Risk Assessment', **FONT_TITLE)
        ax.tick_params(**FONT_TICK)

        legend_items = [
            mpatches.Patch(color=RISK_COLORS['Critical'], label='Critical  ≥ 75'),
            mpatches.Patch(color=RISK_COLORS['High'],     label='High      ≥ 50'),
            mpatches.Patch(color=RISK_COLORS['Medium'],   label='Medium    ≥ 25'),
            mpatches.Patch(color=RISK_COLORS['Low'],      label='Low        < 25'),
        ]
        ax.legend(handles=legend_items, fontsize=8.5, facecolor=BG_FIG,
                  edgecolor=C_SPINE, frameon=True, loc='lower right')

        watermark(fig)
        plt.tight_layout()

        return jsonify({'graph': buf_to_b64(fig)})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(port=5001, debug=True, host='0.0.0.0')