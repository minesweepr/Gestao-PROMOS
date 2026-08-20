document.addEventListener('click', function (event){
    const alt=event.target.closest('[data-menu]');
    if(alt){
        const menu=document.getElementById(alt.dataset.menu);
        const aberto=menu.classList.contains('visivel');
        //fecha tudo que estava aberto
        document.querySelectorAll('.menu.visivel').forEach(m => m.classList.remove('visivel'));
        //abre só o clicado
        if(!aberto) menu.classList.add('visivel');
        return
    }
    //fehca ao clicar fora
    if(!event.target.closest('.menu')) document.querySelectorAll('.menu.visivel').forEach(m => m.classList.remove('visivel'));
});