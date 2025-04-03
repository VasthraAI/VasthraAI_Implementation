import React, { useState, useEffect } from "react";
import Navbar from "./Navbar";
import { useNavigate } from "react-router-dom";

const ViewDesigns = () => {
    const [generatedImage, setGeneratedImage] = useState(null);
    const [originalSketch, setOriginalSketch] = useState(null);
    const navigate = useNavigate();
    
    useEffect(() => {
        // Retrieve design data from sessionStorage
        const designData = sessionStorage.getItem("generatedDesign");
        if (designData) {
            try {
                const { generated_image, original_sketch } = JSON.parse(designData);
                setGeneratedImage(generated_image);
                setOriginalSketch(original_sketch);
            } catch (error) {
                console.error("Error parsing design data:", error);
                navigate("/");
            }
        } else {
            // No design found, redirect to upload page
            navigate("/");
        }
    }, [navigate]);

    const handleNewDesign = () => {
        navigate("/");
    };

    const handleDownload = () => {
        if (!generatedImage) return;
        
        const fullUrl = `http://localhost:8000${generatedImage}`;
        
        fetch(fullUrl)
            .then(response => response.blob())
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const link = document.createElement("a");
                link.href = url;
                link.download = 'vasthra-design.png';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                window.URL.revokeObjectURL(url);
            })
            .catch(error => {
                console.error("Error downloading image:", error);
            });
    };

    return (
        <div className="min-h-screen bg-cover bg-center">
            <Navbar />
            <title>View Designs</title>
            <div className="flex flex-col md:flex-row items-center justify-center p-10 gap-8">
                {/* Display Area */}
                <div className="md:w-3/4 border-3 p-6 flex flex-col items-center justify-center text-gray-600 bg-white rounded-lg transition-all w-full">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full">
                        {/* Original Sketch */}
                        <div className="flex flex-col items-center">
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">Original Sketch</h3>
                            {originalSketch ? (
                                <img 
                                    src={`http://localhost:8000${originalSketch}`} 
                                    alt="Original Sketch" 
                                    className="object-cover w-full h-auto max-h-80 rounded-lg" 
                                />
                            ) : (
                                <p>Loading sketch...</p>
                            )}
                        </div>
                        
                        {/* Generated Design */}
                        <div className="flex flex-col items-center">
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">Generated Design</h3>
                            {generatedImage ? (
                                <img 
                                    src={`http://localhost:8000${generatedImage}`} 
                                    alt="Generated Design" 
                                    className="object-cover w-full h-auto max-h-80 rounded-lg" 
                                />
                            ) : (
                                <p>Loading generated design...</p>
                            )}
                        </div>
                    </div>
                </div>

                {/* Right Section */}
                <div className="md:w-1/4 text-center md:text-left">
                    <h2 className="text-2xl font-bold text-gray-900">Your Batik Design</h2>
                    <p className="text-gray-900 mt-4">
                        Here is your generated batik design. You can download it or create a new design.
                    </p>
                    
                    {/* Buttons */}
                    <div className="mt-6 flex gap-4">
                        <button 
                            className="bg-gray-500 text-white px-6 py-2 rounded-lg hover:bg-gray-700 transition"
                            onClick={handleNewDesign}
                        >
                            New Design
                        </button>
                        <button 
                            className="bg-blue-800 text-white px-6 py-2 rounded-lg hover:bg-violet-950 transition"
                            onClick={handleDownload}
                            disabled={!generatedImage}
                        >
                            Download
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ViewDesigns;