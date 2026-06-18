"""
Biogas Simulator Web Server
Flask-based API serving the simulation engine and PDF generation
"""

import os
import sys
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_file, render_template, send_from_directory
from io import BytesIO

# Add engine to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'engine'))
from simulator import run_simulation, BiogasSimulator, AnimalType, DigesterType

app = Flask(__name__, 
    template_folder='templates',
    static_folder='static'
)

# === ROUTES ===

@app.route('/')
def landing():
    """Serve the landing page"""
    return render_template('landing.html')

@app.route('/app')
def app_index():
    """Serve the main application"""
    return render_template('index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

@app.route('/api/simulate', methods=['POST'])
def api_simulate():
    """Run simulation and return results"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['animal_type', 'num_animals', 'digester_type', 'location_state']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        result = run_simulation(
            animal_type=data['animal_type'],
            num_animals=int(data['num_animals']),
            digester_type=data['digester_type'],
            location_state=data['location_state'],
            eletricity_cost_kwh=float(data.get('eletricity_cost_kwh', 0)),
            has_generator=bool(data.get('has_generator', False)),
            generator_power_kw=float(data.get('generator_power_kw', 0)),
            use_credit_carbono=bool(data.get('use_credit_carbono', False))
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pdf', methods=['POST'])
def api_pdf():
    """Generate PDF report"""
    try:
        data = request.get_json()
        simulation = data.get('simulation', {})
        email = data.get('email', '')
        
        # Generate PDF using simple HTML-to-PDF approach
        pdf_buffer = generate_pdf_report(simulation, email)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'relatorio-biogas-{datetime.now().strftime("%Y-%m-%d")}.pdf'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lead', methods=['POST'])
def api_lead():
    """Capture lead for PRO conversion"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        plan = data.get('plan', 'monthly')
        source = data.get('source', 'app')
        
        if not email or '@' not in email:
            return jsonify({'error': 'Email inválido'}), 400
        
        # Store lead in simple JSON file (production: use CRM/Notion/n8n)
        lead = {
            'email': email,
            'plan': plan,
            'source': source,
            'timestamp': datetime.now().isoformat(),
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', '')[:100]
        }
        
        leads_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'leads.json')
        os.makedirs(os.path.dirname(leads_file), exist_ok=True)
        
        leads = []
        if os.path.exists(leads_file):
            with open(leads_file, 'r') as f:
                leads = json.load(f)
        
        leads.append(lead)
        
        with open(leads_file, 'w') as f:
            json.dump(leads, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'message': 'Lead registrado com sucesso',
            'lead_id': len(leads)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/leads/count')
def leads_count():
    """Get lead count (admin only - basic auth in production)"""
    try:
        leads_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'leads.json')
        if os.path.exists(leads_file):
            with open(leads_file, 'r') as f:
                leads = json.load(f)
            return jsonify({
                'total_leads': len(leads),
                'by_plan': {}
            })
        return jsonify({'total_leads': 0, 'by_plan': {}})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })

# === PDF GENERATION ===

def generate_pdf_report(simulation, email):
    """Generate a simple PDF report using HTML + WeasyPrint or fallback"""
    
    try:
        from weasyprint import HTML, CSS
        has_weasyprint = True
    except ImportError:
        has_weasyprint = False
    
    # Build HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{ size: A4; margin: 2cm; }}
            body {{ font-family: 'Helvetica', Arial, sans-serif; color: #1e293b; line-height: 1.6; }}
            .header {{ text-align: center; border-bottom: 3px solid #059669; padding-bottom: 20px; margin-bottom: 30px; }}
            .header h1 {{ color: #059669; font-size: 28px; margin: 0; }}
            .header p {{ color: #64748b; margin: 8px 0 0; }}
            .badge {{ display: inline-block; padding: 8px 20px; border-radius: 20px; font-weight: bold; font-size: 14px; }}
            .badge.viable {{ background: #d1fae5; color: #047857; }}
            .badge.not-viable {{ background: #fee2e2; color: #ef4444; }}
            .section {{ margin: 25px 0; }}
            .section h2 {{ color: #1e293b; font-size: 18px; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; }}
            .kpi-grid {{ display: flex; gap: 15px; margin: 15px 0; }}
            .kpi-box {{ flex: 1; background: #f8fafc; padding: 15px; border-radius: 8px; text-align: center; }}
            .kpi-label {{ font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }}
            .kpi-value {{ font-size: 20px; font-weight: bold; color: #1e293b; margin-top: 5px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 13px; }}
            th {{ background: #f1f5f9; padding: 10px; text-align: left; font-weight: bold; color: #475569; }}
            td {{ padding: 10px; border-bottom: 1px solid #e2e8f0; }}
            .recommendations {{ background: #f8fafc; padding: 15px; border-radius: 8px; }}
            .recommendations li {{ margin: 8px 0; color: #475569; }}
            .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #e2e8f0; text-align: center; font-size: 12px; color: #94a3b8; }}
            .green {{ color: #059669; }}
            .blue {{ color: #0ea5e9; }}
            .orange {{ color: #f59e0b; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>⚡ Biogas Simulator</h1>
            <p>Relatório Técnico de Viabilidade Econômica</p>
            <p style="font-size: 12px; color: #94a3b8;">Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')} | {email}</p>
        </div>
        
        <div style="text-align: center; margin: 20px 0;">
            <span class="badge {'viable' if simulation.get('viavel') else 'not-viable'}">
                {'PROJETO VIÁVEL' if simulation.get('viavel') else 'PROJETO NÃO VIÁVEL'}
            </span>
        </div>
        
        <div class="section">
            <h2>📊 Indicadores Principais</h2>
            <div class="kpi-grid">
                <div class="kpi-box">
                    <div class="kpi-label">Investimento Total</div>
                    <div class="kpi-value blue">R$ {simulation.get('investimento_total', 0):,.2f}</div>
                </div>
                <div class="kpi-box">
                    <div class="kpi-label">Payback</div>
                    <div class="kpi-value orange">{simulation.get('payback_years', 0):.1f} anos</div>
                </div>
                <div class="kpi-box">
                    <div class="kpi-label">ROI Anual</div>
                    <div class="kpi-value green">{simulation.get('roi_annual', 0):.1f}%</div>
                </div>
                <div class="kpi-box">
                    <div class="kpi-label">Energia/Dia</div>
                    <div class="kpi-value">{simulation.get('potential_energy_kwh_day', 0):.1f} kWh</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>⚡ Geração de Energia</h2>
            <table>
                <tr><th>Período</th><th>kWh</th><th>Equivalente</th></tr>
                <tr><td>Diária</td><td>{simulation.get('potential_energy_kwh_day', 0):.1f}</td><td>{simulation.get('potential_energy_kwh_day', 0) / 3.5:.0f} residências</td></tr>
                <tr><td>Mensal</td><td>{simulation.get('potential_energy_kwh_month', 0):,.0f}</td><td>R$ {simulation.get('economia_mensal_eletricidade', 0):,.2f}</td></tr>
                <tr><td>Anual</td><td>{simulation.get('potential_energy_kwh_year', 0):,.0f}</td><td>R$ {simulation.get('economia_anual_eletricidade', 0):,.2f}</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h2>💰 Análise Financeira</h2>
            <table>
                <tr><th>Item</th><th>Valor Anual</th></tr>
                <tr><td>Economia com energia</td><td>R$ {simulation.get('economia_anual_eletricidade', 0):,.2f}</td></tr>
                <tr><td>Crédito de carbono</td><td>R$ {simulation.get('credito_carbono_valor_anual', 0):,.2f}</td></tr>
                <tr><td><strong>Receita total</strong></td><td><strong>R$ {simulation.get('receita_total_anual', 0):,.2f}</strong></td></tr>
                <tr><td>Lucro líquido</td><td>R$ {simulation.get('lucro_liquido_anual', 0):,.2f}</td></tr>
                <tr><td>VPL (10 anos, 10%)</td><td>R$ {simulation.get('vpl_10anos', 0):,.2f}</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h2>🏭 Produção de Biogás</h2>
            <table>
                <tr><th>Métrica</th><th>Valor Diário</th></tr>
                <tr><td>Dejetos</td><td>{simulation.get('daily_dejeto_m3', 0):.2f} m³</td></tr>
                <tr><td>Biogás bruto</td><td>{simulation.get('daily_biogas_m3', 0):.1f} m³</td></tr>
                <tr><td>Metano (CH₄)</td><td>{simulation.get('daily_ch4_m3', 0):.1f} m³</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h2>🔀 Comparativo por Tipo de Biodigestor</h2>
            <table>
                <tr><th>Tipo</th><th>Investimento</th><th>Payback</th><th>ROI</th><th>Status</th></tr>
    """
    
    for cenario in simulation.get('cenarios', []):
        status = 'VIÁVEL' if cenario.get('viavel') else 'NÃO VIÁVEL'
        html_content += f"""
                <tr>
                    <td><strong>{cenario.get('tipo', '').capitalize()}</strong></td>
                    <td>R$ {cenario.get('investimento', 0):,.2f}</td>
                    <td>{cenario.get('payback_anos', 0):.1f} anos</td>
                    <td>{cenario.get('roi', 0):.0f}%</td>
                    <td>{status}</td>
                </tr>
        """
    
    html_content += """
            </table>
        </div>
        
        <div class="section">
            <h2>💡 Recomendações Técnicas</h2>
            <div class="recommendations">
                <ul>
    """
    
    for rec in simulation.get('recomendacoes', []):
        html_content += f"<li>{rec}</li>"
    
    html_content += f"""
                </ul>
            </div>
        </div>
        
        <div class="footer">
            <p>Biogas Simulator v1.0 — Desenvolvido com stack 100% local (Python + Ollama)</p>
            <p>Este relatório é uma simulação técnica. Consulte um engenheiro especializado para projeto executivo.</p>
        </div>
    </body>
    </html>
    """
    
    if has_weasyprint:
        # Use WeasyPrint for proper PDF generation
        pdf_buffer = BytesIO()
        HTML(string=html_content).write_pdf(pdf_buffer)
        pdf_buffer.seek(0)
        return pdf_buffer
    else:
        # Fallback: return HTML as "PDF" (browser will handle)
        # Or use a simple text-based approach
        pdf_buffer = BytesIO()
        pdf_buffer.write(html_content.encode('utf-8'))
        pdf_buffer.seek(0)
        return pdf_buffer

# === MAIN ===

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Biogas Simulator v1.0 starting on http://0.0.0.0:{port}")
    print(f"📊 API endpoints: /api/simulate, /api/pdf, /api/health")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
