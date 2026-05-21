function copyPrevious(button) {
  const text = button.previousElementSibling?.innerText || "";
  navigator.clipboard.writeText(text);
  button.innerText = "Copied";
  setTimeout(() => { button.innerText = "Copy"; }, 1200);
}
