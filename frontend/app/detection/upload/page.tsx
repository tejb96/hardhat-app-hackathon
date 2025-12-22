'use client';
import { useState } from "react";
import FileUpload from '@/components/file-upload'

const UploadImage = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const sendRequest = async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await fetch("http://localhost:8000/detect", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to upload image");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "ppe_report.pdf";
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error uploading file:", error);
      alert("There was an error uploading the file. Please try again.");
    }
  };
  return (
    <div className="flex flex-col items-center justify-center min-h-screen px-1">
         {selectedFile ? <h1 className="text-3xl font-bold mb-1">Send Image for PPE Detection</h1> 
        : <h1 className="text-3xl font-bold mb-1">Upload Image for PPE Detection</h1>}
        <FileUpload buttonText="Submit for PPE Detection" onSubmit={sendRequest} selectedFile={selectedFile} setSelectedFile={setSelectedFile} />
    </div>
  )
}

export default UploadImage