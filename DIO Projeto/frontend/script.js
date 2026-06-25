const botoesNiveis = document.querySelectorAll(".nivel li");
const botoesCategorias = document.querySelectorAll(".categoria li");
const inputEntrada = document.getElementById("prompt");
const botao = document.querySelector(".botao-otimizar");

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

    console.log("Botão funcionando!")
    console.log("Texto usuario: ", textoUsuario)
    console.log("Nível Desejado:", nivelSelecionado);
    console.log("Categoria:", categoriaSelecionada);
    
    inputEntrada.value = ""
})