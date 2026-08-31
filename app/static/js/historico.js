function filtrarHistorico(filtro, valor) {
    const url = new URL(window.location.href);

    if (valor === "todos") {
        url.searchParams.delete(filtro);
    } else {
        const valorAtual = url.searchParams.get(filtro);

        if (valorAtual === valor) {
            // Clicou novamente no filtro selecionado
            url.searchParams.delete(filtro);
        } else {
            url.searchParams.set(filtro, valor);
        }
    }

    window.location.href = url.toString();
}

/*TODO: Buscar uma forma mais otimizada de fazer essa filtragem */