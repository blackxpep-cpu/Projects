const botoesNiveis = document.querySelectorAll(".nivel li");
const botoesCategorias = document.querySelectorAll(".categoria li");
const inputEntrada = document.getElementById("prompt");
const botao = document.querySelector(".botao-otimizar");
const resultado = document.querySelector(".resultadoPrompt")
const header = document.querySelector("header");
const main = document.querySelector("main");
const sectionResultado = document.querySelector(".resultado");
const botaoNovaOtm = document.querySelector(".botao-novaOtm")

let nivelSelecionado = "Iniciante";
let categoriaSelecionada = "Programação";

botoesNiveis.forEach((botaoN) => {
    botaoN.addEventListener("click", () => {
        nivelSelecionado = botaoN.textContent;

        botoesNiveis.forEach((b) => {
            b.classList.remove("active");
        });

        botaoN.classList.add("active");
    })
})

botoesCategorias.forEach((botaoC) => {
    botaoC.addEventListener("click", () => {
        categoriaSelecionada = botaoC.textContent;

        botoesCategorias.forEach((b) => {
            b.classList.remove("active");
        });

        botaoC.classList.add("active")
    })
})

botao.addEventListener("click", (evento) => {
    // comando para não recarregar a página
    evento.preventDefault();

    let textoUsuario = inputEntrada.value;

    const pacote = {
        texto: textoUsuario,
        nivel: nivelSelecionado,
        categoria: categoriaSelecionada

    };

    botao.textContent = "Otimizando...";
    botao.disabled = true;

    fetch("http://127.0.0.1:5000/otimizar", {
        method: "POST",

        headers: {
            "Content-Type": "application/json" // Avisando que o pacote é um JSON
        },

        body: JSON.stringify(pacote)
    })
        .then((resposta) => resposta.json())
        .then((dadosDeVolta) => {

            if (dadosDeVolta.status === "erro") {
                alert(dadosDeVolta.mensagemErro);

                botao.textContent = "Otimizar";
                botao.disabled = false;

                return;
            }

            resultado.value = dadosDeVolta.prompt_pronto;

            header.style.display = "none";
            main.style.display = "none";
            sectionResultado.style.display = "flex";

            botao.disabled = true;
            inputEntrada.value = ""
        })

        .catch((erro) => {
            console.error("Erro: ", erro);

            botao.textContent = "Otimizar";
            botao.disabled = false;
        });
})

botaoNovaOtm.addEventListener("click", () => {

    sectionResultado.style.display = "none";

    header.style.display = "flex";
    main.style.display = "flex";

    resultado.value = "";
    inputEntrada.value = "";

    botao.disabled = false;
    botao.textContent = "Otimizar"
})