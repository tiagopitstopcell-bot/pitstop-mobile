import base64
import os
import sqlite3
import urllib.parse
from datetime import datetime

import pandas as pd
import streamlit as st
from database import init_db

NOME_LOGO = 'IMG-20260924-WA0001.jpg'

st.set_page_config(
    page_title='PitStop Cell',
    page_icon='📱',
    layout='centered',
    initial_sidebar_state='collapsed',
)

init_db()


def conectar_db():
  return sqlite3.connect('pitstop.db')


def carregar_config():
  conn = conectar_db()
  cursor = conn.cursor()
  cursor.execute(
      'SELECT nome_loja, telefone, endereco, cidade, cnpj, link_google FROM'
      ' configuracoes LIMIT 1'
  )
  cfg = cursor.fetchone()
  conn.close()
  if cfg:
    return {
        'nome': cfg[0],
        'telefone': cfg[1],
        'endereco': cfg[2],
        'cidade': cfg[3],
        'cnpj': cfg[4],
        'link_google': (
            cfg[5] if cfg[5] else 'https://maps.google.com/?q=PitStop+Cell'
        ),
    }
  return {
      'nome': 'PitStop Cell',
      'telefone': '(48) 99999-9999',
      'endereco': 'Rua Principal',
      'cidade': 'Palhoça - SC',
      'cnpj': '00.000.000/0001-00',
      'link_google': 'https://maps.google.com/?q=PitStop+Cell',
  }


if 'pagina' not in st.session_state:
  st.session_state.pagina = 'Início'

if 'impressao_os' not in st.session_state:
  st.session_state.impressao_os = None

if 'ultima_venda' not in st.session_state:
  st.session_state.ultima_venda = None

logo_base64 = ''
if os.path.exists(NOME_LOGO):
  with open(NOME_LOGO, 'rb') as image_file:
    logo_base64 = base64.b64encode(image_file.read()).decode()

# --- CSS BASE PITSTOP CELL ---
st.markdown(
    f"""
    <style>
    [data-testid="stSidebar"] {{ display: none; }}
    header {{ visibility: hidden; }}

    .top-header {{
        background-color: #2563eb;
        padding: 12px 15px;
        color: white !important;
        display: flex;
        align-items: center;
        gap: 12px;
        border-radius: 0 0 12px 12px;
        margin-top: -60px;
        margin-bottom: 20px;
        box-shadow: 0px 3px 6px rgba(0,0,0,0.1);
    }}
    .top-header p, .top-header span {{
        color: #ffffff !important;
    }}
    .logo-circulo {{
        width: 48px;
        height: 48px;
        border-radius: 50%;
        object-fit: cover;
        background-color: #ffffff;
        border: 2px solid #ffffff;
    }}
    div.stButton > button {{
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 12px !important;
        padding: 18px 10px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.05) !important;
        width: 100% !important;
    }}
    .card-item {{
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        margin-bottom: 12px;
    }}
    .card-aniversario {{
        background-color: #fdf2f8;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
        border: 1px solid #f472b6;
        margin-bottom: 12px;
    }}
    </style>
""",
    unsafe_allow_html=True,
)

loja = carregar_config()

tag_img = (
    f'<img src="data:image/jpeg;base64,{logo_base64}" class="logo-circulo">'
    if logo_base64
    else (
        '<div class="logo-circulo"'
        ' style="display:flex;align-items:center;justify-content:center;color:#2563eb;font-weight:bold;">PS</div>'
    )
)

st.markdown(
    f"""
    <div class="top-header">
        {tag_img}
        <div>
            <p style="font-size:18px; font-weight:bold; margin:0;">{loja['nome']}</p>
            <p style="font-size:12px; margin:0; opacity:0.9;">Assistência Técnica e Celulares</p>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)


# ==========================================
# 🏠 TELA INICIAL
# ==========================================
if st.session_state.pagina == 'Início':

  col1, col2 = st.columns(2)

  with col1:
    if st.button('📋\n\nOrdem Serviço', use_container_width=True):
      st.session_state.pagina = 'OS_LISTA'
      st.rerun()

    if st.button('👥\n\nClientes', use_container_width=True):
      st.session_state.pagina = 'CLIENTES'
      st.rerun()

    if st.button('🛒\n\nProdutos', use_container_width=True):
      st.session_state.pagina = 'PRODUTOS'
      st.rerun()

  with col2:
    if st.button('🆕\n\nNova OS', use_container_width=True):
      st.session_state.pagina = 'NOVA_OS'
      st.rerun()

    if st.button('💵\n\nVenda Rápida', use_container_width=True):
      st.session_state.pagina = 'VENDA_RAPIDA'
      st.rerun()

    if st.button('⚙️\n\nConfig. da Loja', use_container_width=True):
      st.session_state.pagina = 'CONFIG_LOJA'
      st.rerun()


# ==========================================
# ⚙️ CONFIGURAÇÕES DA LOJA
# ==========================================
elif st.session_state.pagina == 'CONFIG_LOJA':
  if st.button('← Voltar ao Início'):
    st.session_state.pagina = 'Início'
    st.rerun()

  st.subheader('⚙️ Dados da Loja e Google Maps')

  with st.form('form_config_loja'):
    novo_nome = st.text_input('Nome da Loja', value=loja['nome'])
    novo_tel = st.text_input('Telefone / WhatsApp', value=loja['telefone'])
    novo_end = st.text_input('Endereço', value=loja['endereco'])
    nova_cid = st.text_input('Cidade / Estado', value=loja['cidade'])
    novo_cnpj = st.text_input('CNPJ / CPF', value=loja['cnpj'])
    novo_link = st.text_input(
        'Link do Google Maps para Avaliação', value=loja['link_google']
    )

    salvar_cfg = st.form_submit_button('💾 Salvar Alterações', type='primary')

    if salvar_cfg:
      conn = conectar_db()
      cursor = conn.cursor()
      cursor.execute('DELETE FROM configuracoes')
      cursor.execute(
          'INSERT INTO configuracoes (nome_loja, telefone, endereco, cidade,'
          ' cnpj, link_google) VALUES (?, ?, ?, ?, ?, ?)',
          (novo_nome, novo_tel, novo_end, nova_cid, novo_cnpj, novo_link),
      )
      conn.commit()
      conn.close()
      st.success('✅ Configurações atualizadas!')
      st.rerun()


# ==========================================
# 👥 CLIENTES & LEMBRETE DE ANIVERSÁRIO
# ==========================================
elif st.session_state.pagina == 'CLIENTES':
  if st.button('← Voltar ao Início'):
    st.session_state.pagina = 'Início'
    st.rerun()

  st.subheader('👥 Cadastro e Gestão de Clientes')

  hoje_str = datetime.now().strftime('%d/%m')
  conn = conectar_db()
  cursor = conn.cursor()
  cursor.execute(
      'SELECT nome, telefone, data_nascimento FROM clientes WHERE'
      ' data_nascimento = ?',
      (hoje_str,),
  )
  aniversariantes_hoje = cursor.fetchall()

  if aniversariantes_hoje:
    st.markdown(
        f"""
            <div style="background-color:#fdf2f8; border:2px solid #db2777; padding:15px; border-radius:10px; margin-bottom:20px;">
                <h4 style="color:#db2777; margin:0 0 10px 0;">🎉🎂 ANIVERSARIANTES DE HOJE ({hoje_str})!</h4>
                <p style="margin:0; font-size:14px; color:#374151;">Há clientes fazendo aniversário hoje. Não se esqueça de enviar os parabéns!</p>
            </div>
            """,
        unsafe_allow_html=True,
    )
    for an_nome, an_tel, an_nasc in aniversariantes_hoje:
      st.markdown(f"👉 **{an_nome}** (Tel: {an_tel if an_tel else 'N/I'})")
      if an_tel:
        t_l = ''.join(filter(str.isdigit, an_tel))
        if not t_l.startswith('55'):
          t_l = '55' + t_l
        m_hoje = (
            f"Olá {an_nome}! A equipe da *{loja['nome']}* te deseja um Feliz"
            ' Aniversário! 🎉🎂 Muitas felicidades, saúde e sucesso! Passando'
            ' para lembrar que você é um cliente muito especial para nós.'
        )
        u_hoje = urllib.parse.quote(m_hoje)
        st.markdown(
            f"""<a href="https://wa.me/{t_l}?text={u_hoje}" target="_blank" style="text-decoration:none;"><div style="background-color:#db2777;color:white;text-align:center;padding:8px;border-radius:8px;font-weight:bold;font-size:13px;margin-bottom:10px;">🎁 Enviar Parabéns de Aniversário Hoje ({an_nasc})</div></a>""",
            unsafe_allow_html=True,
        )
    st.markdown('---')

  with st.form('form_cli_aberto', clear_on_submit=True):
    st.markdown('#### ➕ Cadastrar Novo Cliente')
    nome = st.text_input('Nome Completo do Cliente')
    tel = st.text_input('Telefone / WhatsApp')
    cpf = st.text_input('CPF / CNPJ')
    endereco = st.text_input('Endereço Completo')
    email = st.text_input('E-mail')
    nascimento = st.text_input(
        'Data de Nascimento (Ex: 25/12)', placeholder='DD/MM'
    )
    obs = st.text_area('Observações sobre o Cliente')
    btn_c = st.form_submit_button('💾 Salvar Cliente', type='primary')

    if btn_c:
      if nome:
        cursor.execute(
            'INSERT INTO clientes (nome, telefone, cpf_cnpj, endereco, email,'
            ' data_nascimento, observacoes) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (nome, tel, cpf, endereco, email, nascimento, obs),
        )
        conn.commit()
        st.success(f"✅ Cliente '{nome}' cadastrado com sucesso!")
        st.rerun()
      else:
        st.error('Por favor, digite o nome do cliente.')

  st.markdown('---')
  st.subheader('📜 Todos os Clientes Cadastrados')

  cursor.execute(
      'SELECT id, nome, telefone, cpf_cnpj, endereco, data_nascimento,'
      ' observacoes FROM clientes ORDER BY nome'
  )
  clientes_cad = cursor.fetchall()
  conn.close()

  if clientes_cad:
    for cid, cn, ct, ccpf, cend, cnasc, cobs in clientes_cad:
      is_hoje = cnasc == hoje_str
      estilo_card = 'card-aniversario' if is_hoje else 'card-item'

      st.markdown(
          f"""
                <div class="{estilo_card}">
                    <b>👤 {cn}</b> { '🎉 <span style="color:#db2777; font-weight:bold;">(ANIVERSÁRIO HOJE!)</span>' if is_hoje else ''}<br>
                    📞 Tel: {ct if ct else 'N/I'} | 🎂 Nasc: {cnasc if cnasc else 'Não informada'}<br>
                    📍 End: {cend if cend else 'N/I'}<br>
                    📝 Obs: {cobs if cobs else 'Nenhuma'}
                </div>
                """,
          unsafe_allow_html=True,
      )

      if ct:
        t_limpo = ''.join(filter(str.isdigit, ct))
        if not t_limpo.startswith('55'):
          t_limpo = '55' + t_limpo
        msg_parabens = (
            f"Olá {cn}! A equipe da *{loja['nome']}* deseja a você um Feliz"
            ' Aniversário! 🎉🎂 Muitas felicidades e sucesso! Conte sempre com'
            ' a nossa assistência.'
        )
        url_parabens = urllib.parse.quote(msg_parabens)
        st.markdown(
            f"""<a href="https://wa.me/{t_limpo}?text={url_parabens}" target="_blank" style="text-decoration:none;"><div style="background-color:#ec4899;color:white;text-align:center;padding:8px;border-radius:8px;font-weight:bold;font-size:13px;margin-bottom:15px;">🎂 Mandar Parabéns no WhatsApp {f'({cnasc})' if cnasc else ''}</div></a>""",
            unsafe_allow_html=True,
        )
      st.divider()
  else:
    st.info('Nenhum cliente cadastrado.')


# ==========================================
# 📋 ORDENS DE SERVIÇO
# ==========================================
elif st.session_state.pagina == 'OS_LISTA':
  col_back, col_new = st.columns([2, 1])
  with col_back:
    if st.button('← Voltar ao Início'):
      st.session_state.pagina = 'Início'
      st.rerun()
  with col_new:
    if st.button('➕ Nova OS'):
      st.session_state.pagina = 'NOVA_OS'
      st.rerun()

  st.subheader('📋 Ordens de Serviço')

  busca = st.text_input('🔍 Buscar por OS ou Cliente')
  somente_andamento = st.toggle('Apenas OS em andamento', value=True)

  conn = conectar_db()
  cursor = conn.cursor()
  query = """
        SELECT o.id, o.data_entrada, o.previsao_saida, c.nome, o.aparelho, o.status, o.total, o.defeito, o.cor, c.telefone, o.data_entrega
        FROM ordens o
        LEFT JOIN clientes c ON o.cliente_id = c.id
        WHERE 1=1
    """
  params = []
  if busca:
    query += (
        ' AND (c.nome LIKE ? OR o.aparelho LIKE ? OR CAST(o.id AS TEXT) = ?)'
    )
    params.extend([f'%{busca}%', f'%{busca}%', busca])
  if somente_andamento:
    query += (
        " AND o.status NOT IN ('Pronto / Concluído', 'Entregue', 'Cancelado')"
    )
  query += ' ORDER BY o.id DESC'
  cursor.execute(query, params)
  ordens = cursor.fetchall()
  conn.close()

  if ordens:
    for (
        os_id,
        dt_in,
        dt_out,
        cliente,
        aparelho,
        status,
        total,
        defeito,
        cor,
        tel,
        dt_entrega,
    ) in ordens:
      st.markdown(
          f"""
                <div class="card-item">
                    <div style="display:flex; justify-content:space-between;">
                        <b>OS Nº: #{os_id}</b>
                        <span style="background-color:#2563eb; color:white; padding:2px 8px; border-radius:10px; font-size:12px;">{status}</span>
                    </div>
                    <div style="font-size:13px; color:#374151; margin-top:5px;">
                        <b>Cliente:</b> {cliente if cliente else 'S/ Cadastro'} ({tel if tel else 'S/ Tel'})<br>
                        <b>Aparelho:</b> {aparelho} {f'({cor})' if cor else ''}<br>
                        <b>Defeito:</b> {defeito}<br>
                        <b>Entrada:</b> {dt_in} | <b>Entrega:</b> {dt_entrega if dt_entrega else 'Pendente'}<br>
                        <b>Total:</b> <span style="color:#16a34a; font-weight:bold;">R$ {total:.2f}</span>
                    </div>
                </div>
                """,
          unsafe_allow_html=True,
      )

      lista_status_opcoes = [
          'Em orçamento',
          'Aguardando aprovação do cliente',
          'Aguardando peça',
          'Em andamento',
          'Pronto / Concluído',
          'Entregue',
          'Cancelado',
      ]
      idx_atual = (
          lista_status_opcoes.index(status)
          if status in lista_status_opcoes
          else 0
      )

      novo_status_col = st.selectbox(
          f'Alterar Status OS #{os_id}',
          lista_status_opcoes,
          index=idx_atual,
          key=f'st_{os_id}',
      )
      if novo_status_col != status:
        conn = conectar_db()
        cursor = conn.cursor()
        dt_entrega_agora = (
            datetime.now().strftime('%d/%m/%Y')
            if novo_status_col in ['Entregue', 'Pronto / Concluído']
            else None
        )
        if dt_entrega_agora:
          cursor.execute(
              'UPDATE ordens SET status = ?, data_entrega = ? WHERE id = ?',
              (novo_status_col, dt_entrega_agora, os_id),
          )
        else:
          cursor.execute(
              'UPDATE ordens SET status = ? WHERE id = ?',
              (novo_status_col, os_id),
          )
        conn.commit()
        conn.close()
        st.success(f'Status atualizado para: {novo_status_col}')
        st.rerun()

      c_act1, c_act2 = st.columns(2)
      with c_act1:
        if st.button(f'🖨️ Imprimir #{os_id}', key=f'pr_{os_id}'):
          st.session_state.impressao_os = os_id
      with c_act2:
        if tel:
          t_limpo = ''.join(filter(str.isdigit, tel))
          if not t_limpo.startswith('55'):
            t_limpo = '55' + t_limpo

          if novo_status_col in ['Pronto / Concluído', 'Entregue']:
            msg = (
                f'Olá {cliente}!*\n\nTemos ótimas notícias! O seu aparelho'
                f' *{aparelho}* (OS #{os_id}) está pronto e testado!\n\nValor'
                f' total: *R$ {total:.2f}*.\n\nPode vir retirá-lo na'
                f" *{loja['nome']}*! 📱✨\n\nFicamos muito felizes em atendê-lo."
                ' Se puder nos deixar uma avaliação e um feedback sobre o nosso'
                ' atendimento no Google, nos ajudará demais:\n⭐ Avalie-nos'
                f" aqui: {loja['link_google']}\n\nAguardamos seu retorno!"
            )
          else:
            msg = (
                f'Olá {cliente}, aqui é da *{loja["nome"]}*! Passando para'
                ' atualizar sobre a sua Ordem de Serviço'
                f' #{os_id} ({aparelho}). Situação atual: *{novo_status_col}*.'
                f' Valor total: R$ {total:.2f}. Qualquer dúvida estamos à'
                ' disposição!'
            )

          msg_url = urllib.parse.quote(msg)
          st.markdown(
              f"""<a href="https://wa.me/{t_limpo}?text={msg_url}" target="_blank" style="text-decoration:none;"><div style="background-color:#22c55e;color:white;text-align:center;padding:10px;border-radius:8px;font-weight:bold;font-size:14px;margin-top:2px;">💬 Enviar WhatsApp</div></a>""",
              unsafe_allow_html=True,
          )
        else:
          st.caption('Sem telefone cadastrado.')

      st.divider()

    if st.session_state.impressao_os:
      os_sel = st.session_state.impressao_os
      st.markdown('---')
      st.subheader(f'🖨️ Comprovante — OS #{os_sel}')

      tipo_imp = st.radio(
          'Formato de Impressão:',
          ['Térmica (Cupom)', 'Impressão A4 (Completa)'],
          horizontal=True,
      )

      conn = conectar_db()
      cursor = conn.cursor()
      cursor.execute(
          """
                SELECT o.id, o.data_entrada, o.previsao_saida, c.nome, c.cpf_cnpj, c.telefone, c.endereco,
                       o.marca, o.aparelho, o.cor, o.imei, o.acessorios, o.defeito,
                       o.total, o.garantia, o.condicao_pagamento, o.status, o.data_entrega
                FROM ordens o LEFT JOIN clientes c ON o.cliente_id = c.id WHERE o.id = ?
            """,
          (os_sel,),
      )
      d = cursor.fetchone()
      conn.close()

      if d:
        dt_ent_str = d[17] if d[17] else 'Em andamento / Pendente'
        if tipo_imp == 'Térmica (Cupom)':
          recibo = f"""
========================================
             {loja['nome'].upper()}
       {loja['cidade']} | Fone: {loja['telefone']}
========================================
ORDEM DE SERVIÇO Nº: {d[0]}
Status: {d[16]}
Data Entrada: {d[1]}
Data Entrega: {dt_ent_str}
----------------------------------------
CLIENTE: {d[3] if d[3] else 'Não informado'}
FONE: {d[5] if d[5] else 'Não informado'}
----------------------------------------
EQUIPAMENTO: {d[7]} {d[8]} ({d[9] if d[9] else 'Cor N/I'})
DEFEITO: {d[12]}
----------------------------------------
VALOR TOTAL: R$ {d[13]:.2f}
Pagamento: {d[15]} | Garantia: {d[14]}
========================================
TERMO DE GARANTIA:
- Cobre apenas o serviço/peça executada.
- Perde validade por quedas, água ou mau uso.
- Aparelhos não retirados em 90 dias serão
considerados abandonados (Art. 1.275 Código Civil).
========================================
"""
        else:
          recibo = f"""
==================================================
                   {loja['nome'].upper()}
        Assistência Técnica e Celulares
   Fone: {loja['telefone']} | {loja['cidade']}
==================================================
            Ordem de Serviço Nº {d[0]}
Status Atual: {d[16]}
--------------------------------------------------
Garantia Até: {d[14]}
Data Entrada: {d[1]}      Data Entrega: {dt_ent_str}
--------------------------------------------------
Cliente: {d[3] if d[3] else 'Não informado'}
Endereço: {d[6] if d[6] else 'Não informado'}
CPF/CNPJ: {d[4] if d[4] else 'Não informado'}
Fone: {d[5] if d[5] else 'Não informado'}
--------------------------------------------------
Modelo: {d[8]} ({d[9] if d[9] else 'Cor N/I'})  Acessórios: {d[11] if d[11] else 'Nenhum'}
Marca: {d[7]}                    Tipo: Manutenção
--------------------------------------------------
Reclamação / Defeito:
{d[12]}
--------------------------------------------------
Condição de pagamento: {d[15]}
Observação: Aparelho deixado para orçamento/reparo.

TERMO DE GARANTIA E CONDIÇÕES:
1. A garantia cobre apenas defeitos da peça substituída ou serviço executado.
2. A garantia PERDE A VALIDADE em caso de: Quedas, impactos, contato com água/líquidos, mau uso, violação ou remoção de lacres de segurança.
3. Aparelhos não retirados no prazo de 90 dias após a conclusão do serviço serão considerados abandonados e poderão ser vendidos para cobrir custos de armazenamento e manutenção, conforme o Código Civil.
==================================================
VALOR TOTAL DO SERVIÇO: R$ {d[13]:.2f}
==================================================
"""
        st.code(recibo, language='text')

      if st.button('Fechar Comprovante'):
        st.session_state.impressao_os = None
        st.rerun()
  else:
    st.info('Nenhuma OS encontrada.')


# ==========================================
# 💵 VENDA RÁPIDA (BALCÃO / CAIXA)
# ==========================================
elif st.session_state.pagina == 'VENDA_RAPIDA':
  if st.button('← Voltar ao Início'):
    st.session_state.pagina = 'Início'
    st.rerun()

  st.subheader('💵 Venda Rápida / Caixa')

  conn = conectar_db()
  cursor = conn.cursor()
  cursor.execute(
      'SELECT id, descricao, preco_venda, quantidade FROM produtos WHERE'
      ' quantidade > 0'
  )
  produtos_disp = cursor.fetchall()
  conn.close()

  if produtos_disp:
    dict_prods = {
        f'{p[1]} (Estoque: {p[3]} - R$ {p[2]:.2f})': p for p in produtos_disp
    }

    with st.form('form_venda_rapida'):
      prod_escolhido = st.selectbox(
          'Selecione o Produto / Peça', list(dict_prods.keys())
      )
      qtd_venda = st.number_input('Quantidade', min_value=1, value=1)
      forma_pg = st.selectbox(
          'Forma de Pagamento',
          ['PIX', 'Dinheiro', 'Cartão de Crédito', 'Cartão de Débito'],
      )
      cliente_venda = st.text_input('Nome do Cliente (Opcional)')

      btn_finalizar_venda = st.form_submit_button(
          '🛒 Concluir Venda', type='primary'
      )

      if btn_finalizar_venda:
        p_id, p_desc, p_preco, p_qtd_atual = dict_prods[prod_escolhido]

        if qtd_venda > p_qtd_atual:
          st.error('Quantidade solicitada maior que o estoque disponível!')
        else:
          total_venda = p_preco * qtd_venda
          dt_hoje = datetime.now().strftime('%d/%m/%Y')

          conn = conectar_db()
          cursor = conn.cursor()
          nova_qtd = p_qtd_atual - qtd_venda
          cursor.execute(
              'UPDATE produtos SET quantidade = ? WHERE id = ?',
              (nova_qtd, p_id),
          )

          cli_str = f' - Cliente: {cliente_venda}' if cliente_venda else ''
          cursor.execute(
              'INSERT INTO caixa (data, tipo, descricao, valor,'
              ' forma_pagamento) VALUES (?, ?, ?, ?, ?)',
              (
                  dt_hoje,
                  'Entrada',
                  f'Venda Balcão: {qtd_venda}x {p_desc}{cli_str}',
                  total_venda,
                  forma_pg,
              ),
          )
          conn.commit()
          conn.close()

          st.session_state.ultima_venda = {
              'desc': f'{qtd_venda}x {p_desc}',
              'valor': total_venda,
              'pg': forma_pg,
              'cli': cliente_venda if cliente_venda else 'Balcão',
              'data': dt_hoje,
          }
          st.success(
              f'✅ Venda de R$ {total_venda:.2f} realizada com sucesso!'
          )

    if st.session_state.ultima_venda:
      v = st.session_state.ultima_venda
      st.markdown('---')
      st.subheader('🖨️ Comprovante da Venda')
      tipo_imp_venda = st.radio(
          'Formato da Venda:',
          ['Térmica (Cupom)', 'Impressão A4'],
          horizontal=True,
      )

      if tipo_imp_venda == 'Térmica (Cupom)':
        recibo_venda = f"""
========================================
             {loja['nome'].upper()}
       {loja['cidade']} | Fone: {loja['telefone']}
========================================
COMPROVANTE DE VENDA RÁPIDA
Data: {v['data']}
Cliente: {v['cli']}
----------------------------------------
Item: {v['desc']}
----------------------------------------
VALOR TOTAL: R$ {v['valor']:.2f}
Forma de Pagamento: {v['pg']}
========================================
Obrigado pela preferência!
========================================
"""
      else:
        recibo_venda = f"""
==================================================
                   {loja['nome'].upper()}
        Assistência Técnica e Celulares
   Fone: {loja['telefone']} | {loja['cidade']}
==================================================
               COMPROVANTE DE VENDA
--------------------------------------------------
Data: {v['data']}           Cliente: {v['cli']}
--------------------------------------------------
Descrição do Item / Produto:
{v['desc']}
--------------------------------------------------
Forma de Pagamento: {v['pg']}
VALOR TOTAL DA VENDA: R$ {v['valor']:.2f}
==================================================
Obrigado pela preferência! Volte sempre!
==================================================
"""
      st.code(recibo_venda, language='text')
  else:
    st.info('Nenhum produto cadastrado com estoque disponível para venda.')


# ==========================================
# 🆕 FORMULÁRIO DE NOVA OS
# ==========================================
elif st.session_state.pagina == 'NOVA_OS':
  if st.button('← Voltar ao Início'):
    st.session_state.pagina = 'Início'
    st.rerun()

  st.subheader('🆕 Cadastrar Nova OS')

  conn = conectar_db()
  cursor = conn.cursor()
  cursor.execute('SELECT id, nome FROM clientes ORDER BY nome')
  lista_cli = cursor.fetchall()
  dict_cli = {nome: cid for cid, nome in lista_cli}
  conn.close()

  st.markdown('### 👤 Cliente')
  opt_cli = st.selectbox(
      'Selecione o Cliente Cadastrado ou crie um novo:',
      ['-- Cadastrar Novo Cliente --'] + list(dict_cli.keys()),
  )

  c_nome, c_tel, c_end, c_email, c_nasc, c_obs = '', '', '', '', '', ''
  if opt_cli == '-- Cadastrar Novo Cliente --':
    c_nome = st.text_input('Nome do Novo Cliente')
    c_tel = st.text_input('Telefone / WhatsApp')
    c_end = st.text_input('Endereço Completo')
    c_email = st.text_input('E-mail')
    c_nasc = st.text_input(
        'Data de Nascimento (Ex: 25/12)', placeholder='DD/MM'
    )
    c_obs = st.text_area('Observações sobre o Cliente')

  with st.form('form_nova_os'):
    st.markdown('---')
    st.markdown('### 📱 Equipamento')
    marca = st.text_input('Marca (Ex: Samsung, Apple, Motorola)')
    aparelho = st.text_input('Modelo do Aparelho (Ex: iPhone 11)')
    cor = st.text_input('Cor do Aparelho')
    imei = st.text_input('IMEI / Nº de Série')
    senha = st.text_input('Senha / Padrão de Desbloqueio')
    acessorios = st.text_input('Acessórios Deixados')
    defeito = st.text_area('Defeito Relatado')

    st.markdown('---')
    st.markdown('### 💰 Valores & Status inicial')
    v_peca = st.number_input('Valor Peças (R$)', min_value=0.0, step=5.0)
    v_obra = st.number_input('Mão de Obra (R$)', min_value=0.0, step=10.0)
    v_desc = st.number_input('Desconto (R$)', min_value=0.0, step=5.0)
    garantia = st.text_input('Garantia', value='90 dias')
    cond_pag = st.selectbox(
        'Forma de Pagamento',
        ['PIX', 'Dinheiro', 'Cartão de Crédito', 'Cartão de Débito'],
    )
    status_inicial = st.selectbox(
        'Status Inicial da OS',
        [
            'Em orçamento',
            'Aguardando aprovação do cliente',
            'Aguardando peça',
            'Em andamento',
            'Pronto / Concluído',
            'Entregue',
        ],
    )

    salvar = st.form_submit_button('💾 Salvar Ordem de Serviço', type='primary')

    if salvar:
      conn = conectar_db()
      cursor = conn.cursor()

      if opt_cli == '-- Cadastrar Novo Cliente --':
        if c_nome:
          cursor.execute(
              'INSERT INTO clientes (nome, telefone, endereco, email,'
              ' data_nascimento, observacoes) VALUES (?, ?, ?, ?, ?, ?)',
              (c_nome, c_tel, c_end, c_email, c_nasc, c_obs),
          )
          cliente_id = cursor.lastrowid
        else:
          cliente_id = None
      else:
        cliente_id = dict_cli[opt_cli]

      total_calc = (v_peca + v_obra) - v_desc
      dt_hoje = datetime.now().strftime('%d/%m/%Y')
      dt_entrega_inicial = (
          dt_hoje
          if status_inicial in ['Pronto / Concluído', 'Entregue']
          else None
      )

      if aparelho and defeito:
        cursor.execute(
            """
                    INSERT INTO ordens (data_entrada, data_entrega, cliente_id, marca, aparelho, cor, imei, senha, acessorios, defeito, valor_peca, mao_de_obra, desconto, total, status, garantia, condicao_pagamento)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
            (
                dt_hoje,
                dt_entrega_inicial,
                cliente_id,
                marca,
                aparelho,
                cor,
                imei,
                senha,
                acessorios,
                defeito,
                v_peca,
                v_obra,
                v_desc,
                total_calc,
                status_inicial,
                garantia,
                cond_pag,
            ),
        )

        if total_calc > 0 and status_inicial in [
            'Pronto / Concluído',
            'Entregue',
        ]:
          cursor.execute(
              'INSERT INTO caixa (data, tipo, descricao, valor,'
              ' forma_pagamento) VALUES (?, ?, ?, ?, ?)',
              (
                  dt_hoje,
                  'Entrada',
                  f'OS #{aparelho} - {c_nome if c_nome else opt_cli}',
                  total_calc,
                  cond_pag,
              ),
          )

        conn.commit()
        st.success('✅ OS Cadastrada com Sucesso!')
        st.session_state.pagina = 'OS_LISTA'
        st.rerun()
      else:
        st.error('Preencha ao menos o Modelo e o Defeito.')

      conn.close()


# ==========================================
# 🛒 PRODUTOS / ESTOQUE
# ==========================================
elif st.session_state.pagina == 'PRODUTOS':
  if st.button('← Voltar ao Início'):
    st.session_state.pagina = 'Início'
    st.rerun()

  st.subheader('🛒 Produtos & Peças em Estoque')

  with st.form('form_prod_aberto', clear_on_submit=True):
    p_desc = st.text_input('Descrição do Produto / Peça')
    p_cat = st.text_input('Categoria (ex: Tela, Bateria, Cabo)')
    p_prec = st.number_input('Preço de Venda (R$)', min_value=0.0)
    p_qtd = st.number_input('Quantidade', min_value=1, value=1)
    btn_prod = st.form_submit_button('💾 Salvar Produto', type='primary')

    if btn_prod and p_desc:
      conn = conectar_db()
      cursor = conn.cursor()
      cursor.execute(
          'INSERT INTO produtos (descricao, categoria, preco_venda, quantidade)'
          ' VALUES (?, ?, ?, ?)',
          (p_desc, p_cat, p_prec, p_qtd),
      )
      conn.commit()
      conn.close()
      st.success('Produto Cadastrado!')
      st.rerun()

  st.markdown('---')
  conn = conectar_db()
  df_prod = pd.read_sql_query(
      "SELECT id AS 'ID', descricao AS 'Descrição', categoria AS 'Categoria',"
      " preco_venda AS 'Preço (R$)', quantidade AS 'Qtd' FROM produtos",
      conn,
  )
  conn.close()

  if not df_prod.empty:
    st.dataframe(df_prod, use_container_width=True)
  else:
    st.info('Nenhum produto em estoque.')


# ==========================================
# 💰 FLUXO DE CAIXA
# ==========================================
elif st.session_state.pagina == 'CAIXA':
  if st.button('← Voltar ao Início'):
    st.session_state.pagina = 'Início'
    st.rerun()

  st.subheader('💰 Fluxo de Caixa')

  conn = conectar_db()
  cursor = conn.cursor()
  cursor.execute("SELECT SUM(valor) FROM caixa WHERE tipo = 'Entrada'")
  ent = cursor.fetchone()[0] or 0.0
  cursor.execute("SELECT SUM(valor) FROM caixa WHERE tipo = 'Saída'")
  sai = cursor.fetchone()[0] or 0.0
  conn.close()

  st.metric('Saldo do Caixa', f'R$ {(ent - sai):.2f}')

  conn = conectar_db()
  df_cx = pd.read_sql_query(
      "SELECT id AS 'Nº', data AS 'Data', tipo AS 'Tipo', descricao AS"
      " 'Descrição', valor AS 'Valor (R$)', forma_pagamento AS 'Pagamento' FROM"
      ' caixa ORDER BY id DESC',
      conn,
  )
  conn.close()

  if not df_cx.empty:
    st.dataframe(df_cx, use_container_width=True)
  else:
    st.info('Nenhuma movimentação registrada.')
