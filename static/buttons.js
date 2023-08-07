const form = document.getElementById("botoes");
const pdfButton = document.getElementById("pdf");
const excelButton = document.getElementById("excel");

pdfButton.addEventListener("click", () => {
  form.action = "/gerar-pdf/";
});

excelButton.addEventListener("click", () => {
  form.action = "/gerar-excel/";
});
