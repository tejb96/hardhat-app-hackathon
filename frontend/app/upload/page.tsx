'use client';
import { useState, useRef, useEffect } from "react";
import FileUpload from '@/components/file-upload'
import { Button } from "@/components/ui/button";

const UploadImage = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [detectionResults, setDetectionResults] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const handleAnalyze = async () => {
    if (!selectedFile) return;

    setIsAnalyzing(true);
    setDetectionResults(null);

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

      const res = await response.json();
      setDetectionResults(res);
    } catch (error) {
      console.error("Error uploading file:", error);
      alert("There was an error uploading the file. Please try again.");
    }
  };

  useEffect(() => {
    if (!selectedFile || !detectionResults || !canvasRef.current) return;

    const img = new Image();
    img.onload = () => {
      const canvas = canvasRef.current!;
      const ctx = canvas.getContext("2d")!;
      
      canvas.width = img.width;
      canvas.height = img.height;
      
      ctx.drawImage(img, 0, 0);

      detectionResults.detections.forEach((det: any) => {
        const [x1, y1, x2, y2] = det.bbox;
        const isSafe = det.class_name === "Hardhat";

        ctx.strokeStyle = isSafe ? "#22c55e" : "#ef4444"; // green or red
        ctx.lineWidth = 4;
        ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

        // const label = `${det.class_name.replace("-", " ")} ${(det.confidence * 100).toFixed(0)}%`;
        // ctx.font = "bold 18px sans-serif";
        // ctx.fillStyle = ctx.strokeStyle;
        // const metrics = ctx.measureText(label);
        // ctx.fillRect(x1, y1 - 30, metrics.width + 12, 30);

        // ctx.fillStyle = "white";
        // ctx.fillText(label, x1 + 6, y1 - 8);
      });
    };
    img.src = URL.createObjectURL(selectedFile);
  }, [selectedFile, detectionResults]);


    return (
    <div className="flex flex-col items-center justify-center min-h-screen px-1">
      <h1 className="text-3xl font-bold mb-1">
        PPE Hardhat Detection
      </h1>

      {/* Upload Section - shown only before analysis */}
      {!detectionResults && (
        <FileUpload
          buttonText={isAnalyzing ? "Analyzing..." : "Analyze Image"}
          onSubmit={handleAnalyze}
          selectedFile={selectedFile}
          setSelectedFile={setSelectedFile}
        />
      )}

      {/* Results Section - shown after detection */}
      {detectionResults && (
        <div className="w-full max-w-2xl mt-8 space-y-8">
          {/* Summary Cards */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-blue-50 rounded-xl p-4 text-center">
              <p className="text-3xl font-bold text-blue-700">
                {detectionResults.summary.total_persons}
              </p>
              <p className="text-sm text-gray-600 mt-1">Total Workers</p>
            </div>

            <div className="bg-green-50 rounded-xl p-4 text-center">
              <p className="text-3xl font-bold text-green-700">
                {detectionResults.summary.wearing_hardhat}
              </p>
              <p className="text-sm text-gray-600 mt-1">Compliant</p>
            </div>

            <div className="bg-red-50 rounded-xl p-4 text-center">
              <p className="text-3xl font-bold text-red-700">
                {detectionResults.summary.missing_hardhat}
              </p>
              <p className="text-sm text-gray-600 mt-1">Violations</p>
            </div>

            <div className="bg-purple-50 rounded-xl p-4 text-center">
              <p className="text-3xl font-bold text-purple-700">
                {detectionResults.summary.average_confidence}%
              </p>
              <p className="text-sm text-gray-600 mt-1">Average Confidence</p>
            </div>

            <div className="col-span-2">
              {/* <Button
                className="w-full rounded-2xl"
                size="lg"
                onClick={handleGenerateReport}
                disabled={isGeneratingReport}
              >
                {isGeneratingReport ? "Generating..." : "Generate PDF Report"}
              </Button> */}
            </div>
          </div>

          {/* Annotated Image */}
          <div className="bg-white rounded-2xl border border-gray-200 p-6">
            <h2 className="text-2xl font-bold text-center mb-4">
              Detection Results
            </h2>

            <div className="flex justify-center">
              <canvas
                ref={canvasRef}
                className="max-w-full h-auto rounded-xl border border-gray-300"
              />
              <div className="mt-4 flex gap-6 text-sm font-medium text-gray-700">
                <div className="flex items-center gap-2">
                  <span className="w-4 h-4 rounded-full bg-red-500 border border-red-700"></span>
                  <span>No Hard Hat</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-4 h-4 rounded-full bg-green-500 border border-green-700"></span>
                  <span>Helmet</span>
                </div>
              </div>
            </div>

            <div className="mt-6 text-center">
              <Button
                variant="outline"
                size="lg"
                className="rounded-2xl"
                onClick={() => {
                  setDetectionResults(null);
                  setSelectedFile(null);
                }}
              >
                Analyze New Image
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default UploadImage