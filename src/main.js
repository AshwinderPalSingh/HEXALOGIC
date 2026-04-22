function reportBootFailure(error) {
  console.error("[HexLogic] Boot failed:", error);
  const loader = document.getElementById("app-loader");
  if (loader) loader.remove();
  const errorBox = document.getElementById("error-box");
  if (errorBox) {
    errorBox.hidden = false;
    errorBox.textContent = "Startup failed. Open DevTools Console for details.";
  }
}

window.addEventListener("unhandledrejection", (event) => {
  reportBootFailure(event.reason || event);
});

window.addEventListener("error", (event) => {
  reportBootFailure(event.error || event.message || event);
});

(async () => {
  try {
    await import("../api/static/sim8051-app.js");
  } catch (error) {
    reportBootFailure(error);
  }
})();

