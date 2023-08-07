// arquivos atalhos_teclado.js

// Evento de teclado global
document.addEventListener("keydown", function (event) {
  // Verifique se a tecla de atalho para o filtro de apps foi pressionada (por exemplo, 'Alt + A')
  if (event.altKey && event.key === "a") {
    var filtroAppsElement = document.getElementById("nav-filter");
    if (filtroAppsElement) {
      filtroAppsElement.focus();
    }
  }

  // Verifique se a tecla de atalho para o primeiro elemento legível foi pressionada (por exemplo, 'Alt + C')
  if (event.altKey && event.key === "z") {
    var divElement = document.getElementById("content");
    if (divElement) {
      var primeiroElemento = divElement.querySelector(
        "a, button, input:not([type='hidden']), select, textarea, [tabindex]:not([tabindex='-1'])"
      );
      if (primeiroElemento) {
        if (
          primeiroElemento.matches("a, button") ||
          primeiroElemento.nodeName === "INPUT"
        ) {
          primeiroElemento.focus();
        }
      }
    }
  }

  if (event.altKey && event.key === "j") {
    var filtroAppsElement = document.getElementById("toggle-nav-sidebar");
    if (filtroAppsElement) {
      filtroAppsElement.click();
    }
  }
});
