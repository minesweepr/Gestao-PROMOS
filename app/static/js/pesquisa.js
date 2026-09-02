document.addEventListener("DOMContentLoaded", () => {
    const input=document.getElementById("input-busca-usuario");
    const listaNomes=document.querySelectorAll(".usuario-nome");

    function pesquisar(){
        const termo=input.value.toLowerCase().trim();

        listaNomes.forEach(card=>{
            const texto=card.innerText.toLowerCase();
            const conteudo=card.closest(".card-retangular");
            conteudo.style.display=texto.includes(termo)?"flex":"none";
        });
    }
    input.addEventListener("input", pesquisar);
    document.querySelector(".fa-search")?.addEventListener("click", pesquisar);
    input.addEventListener("keydown", e => e.key==="Enter" && (e.preventDefault(), pesquisar()));
    pesquisar();
});