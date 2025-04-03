import React, { useState } from "react";
import Navbar from "./Navbar";
import { useNavigate } from "react-router-dom";

const UploadPage = () => {
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const navigate = useNavigate();

  const handleDrop = (event) => {
    event.preventDefault();
    const droppedFile = event.dataTransfer.files[0];
    validateFile(droppedFile);
  };

  const handleFileSelect = (event) => {
    const selectedFile = event.target.files[0];
    validateFile(selectedFile);
  };

  const validateFile = (file) => {
    if (file && (file.type === "image/png" || file.type === "image/jpeg")) {
      setFile(file);
      setError("");
    } else {
      setFile(null);
      setError("Invalid file type. Please upload a PNG or JPEG file.");
    }
  };

  const handleReset = () => {
    setFile(null);
    setError("");
  };

  const handleProceed = async () => {
    if (!file) {
      setError("No file uploaded. Please upload a PNG or JPEG file.");
      return;
    }

    setIsUploading(true);
    setError("");

    // Create FormData and append the file
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/generate/", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to generate design");
      }

      const data = await response.json();

      if (data.success) {
        // Store the image paths in sessionStorage
        sessionStorage.setItem("generatedDesign", JSON.stringify({
          generated_image: data.generated_image,
          original_sketch: data.original_sketch
        }));
        navigate("/view-designs");
      } else {
        setError(data.detail || "Failed to generate design");
      }
    } catch (error) {
      console.error("Error:", error);
      setError("Server error. Please try again later.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-cover bg-center">
      <title>Upload Page</title>
      <Navbar />
      <div className="flex flex-col md:flex-row items-center justify-center p-10 gap-8">
        {/* Drag and Drop Area */}
        <div 
          className="md:w-1/2 border-2 border-dashed p-16 flex flex-col items-center justify-center text-gray-600 cursor-pointer bg-white rounded-lg h-96 transition-all"
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
          onClick={() => document.getElementById("fileInput").click()}
        >
          {file ? (
            <div className="flex flex-col items-center">
              <p className="text-green-600 mb-2">File Uploaded: {file.name}</p>
              <img 
                src={URL.createObjectURL(file)} 
                alt="Preview" 
                className="max-h-40 max-w-full object-contain"
              />
            </div>
          ) : (
            <p>Click to upload or drop your designs here</p>
          )}
          <input 
            type="file" 
            id="fileInput" 
            className="hidden" 
            accept="image/png, image/jpeg"
            onChange={handleFileSelect} 
          />
          {error && <p className="text-red-600 mt-2">{error}</p>}
        </div>

        {/* Right Section */}
        <div className="md:w-1/2 text-center md:text-left">
          <h2 className="text-2xl font-bold text-gray-900">Upload Your Sketch</h2>
          <p className="text-gray-900 mt-4">
            Upload your sketch and VasthraAI will generate a colored batik design for you.
          </p>
          
          {/* Buttons */}
          <div className="mt-6 flex gap-4">
            <button 
              className="bg-gray-500 text-white px-6 py-2 rounded-lg hover:bg-gray-700 transition"
              onClick={handleReset}
              disabled={isUploading}
            >
              Reset
            </button>
            <button 
              className="bg-blue-800 text-white px-6 py-2 rounded-lg hover:bg-violet-950 transition"
              onClick={handleProceed}
              disabled={isUploading}
            >
              {isUploading ? "Processing..." : "Generate Design"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;