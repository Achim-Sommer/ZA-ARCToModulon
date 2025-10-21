const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("fileInput");
const statusBox = document.getElementById("status");
const resultBox = document.getElementById("result");
const downloadLink = document.getElementById("downloadLink");

const MAX_FILE_SIZE_MB = 20;

const humanFileSize = (bytes) => {
  if (!bytes) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  const exponent = Math.min(
    Math.floor(Math.log(bytes) / Math.log(1024)),
    units.length - 1
  );
  const value = bytes / 1024 ** exponent;
  return `${value.toFixed(value >= 10 || exponent === 0 ? 0 : 1)} ${units[exponent]}`;
};

const showStatus = (message, isError = false) => {
  statusBox.textContent = message;
  statusBox.hidden = false;
  statusBox.classList.toggle("error", isError);
  if (isError) {
    resultBox.hidden = true;
  }
};

const clearStatus = () => {
  statusBox.hidden = true;
  statusBox.classList.remove("error");
};

const uploadFile = async (file) => {
  if (!file) {
    return;
  }

  if (!file.name.toLowerCase().endsWith(".csv")) {
    showStatus("Bitte laden Sie ausschließlich CSV-Dateien hoch.", true);
    return;
  }

  if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
    showStatus(
      `Datei ist zu groß (${humanFileSize(file.size)}). Maximal erlaubt sind ${MAX_FILE_SIZE_MB} MB.`,
      true
    );
    return;
  }

  const formData = new FormData();
  formData.append("file", file, file.name);

  showStatus(`Verarbeite „${file.name}”…`);

  try {
    const response = await fetch("/convert", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const payload = await response.json().catch(() => ({}));
      const message = payload.error || `Fehler beim Umwandeln (Status ${response.status}).`;
      showStatus(message, true);
      return;
    }

    const blob = await response.blob();
    const downloadUrl = URL.createObjectURL(blob);

    const fallbackName = "fertig-fuer-modulon.csv";
    const contentDisposition = response.headers.get("Content-Disposition") || "";
    const filenameMatch = contentDisposition.match(/filename="?([^";]+)"?/i);
    const filename = filenameMatch ? filenameMatch[1] : fallbackName;

    downloadLink.href = downloadUrl;
    downloadLink.download = filename;
    resultBox.hidden = false;
    clearStatus();

    // Automatischer Download für schnellen Workflow
    downloadLink.click();
  } catch (error) {
    console.error(error);
    showStatus("Netzwerkfehler. Bitte versuchen Sie es erneut.", true);
  }
};

dropzone.addEventListener("dragover", (event) => {
  event.preventDefault();
  dropzone.classList.add("dragover");
});

dropzone.addEventListener("dragleave", () => {
  dropzone.classList.remove("dragover");
});

dropzone.addEventListener("drop", (event) => {
  event.preventDefault();
  dropzone.classList.remove("dragover");
  const file = event.dataTransfer?.files?.[0];
  uploadFile(file);
});

dropzone.addEventListener("click", () => fileInput.click());

dropzone.addEventListener("keydown", (event) => {
  if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    fileInput.click();
  }
});

fileInput.addEventListener("change", () => {
  const file = fileInput.files?.[0];
  uploadFile(file);
});
