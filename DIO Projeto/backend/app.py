import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv("../.env")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/otimizar", methods=["POST"])
def receber_pedido():

    dados = request.json

    texto_recebido = dados.get("texto")
    nivel_recebido = dados.get("nivel")
    categoria_recebida = dados.get("categoria")
    promptOtimizado = f"""Você é um Engenheiro de Prompts Sênior especializado em maximizar a qualidade das respostas produzidas por modelos de IA.

Sua tarefa é transformar solicitações simples dos usuários em prompts altamente eficazes, claros, específicos e orientados a resultados.

Categoria selecionada: {categoria_recebida}
Nível selecionado: {nivel_recebido}

Solicitação original do usuário:
{texto_recebido}

Analise primeiro a intenção real do usuário.

Regras gerais:

* Preserve o objetivo principal do usuário.
* Nunca altere o significado original.
* Elimine ambiguidades.
* Acrescente contexto relevante quando necessário.
* Defina um papel adequado para a IA executar a tarefa.
* Organize a solicitação de forma profissional.
* Produza prompts que funcionem em ChatGPT, Gemini, Claude e modelos similares.

Se o nível for INICIANTE:

* Reescreva a solicitação de forma clara e objetiva.
* Adicione apenas contexto essencial.
* Mantenha o prompt curto e fácil de usar.

Se o nível for INTERMEDIÁRIO:

* Defina uma persona adequada para a IA.
* Acrescente contexto relevante.
* Defina formato esperado da resposta.
* Sugira melhorias que aumentem a qualidade do resultado.

Se o nível for AVANÇADO:

* Estruture o prompt usando:

  * Papel da IA
  * Objetivo
  * Contexto
  * Restrições
  * Critérios de qualidade
  * Formato de saída
* Antecipe informações que o usuário talvez tenha esquecido de fornecer.
* Inclua instruções para maximizar precisão, profundidade e utilidade.
* Transforme o pedido em um prompt de nível profissional.

Retorne apenas o prompt otimizado, sem explicações adicionais."""

    try:
        modelo = genai.GenerativeModel("gemini-2.5-flash")
        dadosDeVolta = modelo.generate_content(promptOtimizado)

        return jsonify({
            "status": "sucesso", 
            "prompt_pronto": dadosDeVolta.text
        })
        
    except Exception as erro_real:
            erro = str(erro_real)
            
            if "429" in erro or "quota" in erro.lower():
                return jsonify({
                    "status": "erro",
                    "mensagemErro": "Você atingiu o limite gratuito do Gemini. Tente novamente mais tarde."
                })
            
            return jsonify({
                "status": "erro", 
                "mensagemErro": "Ocorreu um erro ao gerar o prompt. Tente novamente."
            })

if __name__ == "__main__":
    app.run(debug=True)