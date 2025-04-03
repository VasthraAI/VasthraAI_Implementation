// import React, { useState } from "react";
import Navbar from "./Navbar";
import { useNavigate } from "react-router-dom";

const ViewDesigns = () => {

    const navigate = useNavigate();
    const handleNewDesign = () =>{
        navigate("/")
    }

    const handleDownload = () => {
        const imageUrls = [
            "src\\assets\\samples\\2f2ba762c9db4434b7df1ce426e0758c.jpg",
            "src\\assets\\samples\\05ca058f615842878768b567bc24271d.jpg",
            "src\\assets\\samples\\7fffd3daccce43008a92674b0e265cf1.jpg"
        ];
        
        imageUrls.forEach((url, index) => {
            const link = document.createElement("a");
            link.href = url;
            link.download = `design-${index + 1}.jpg`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        });
    };

  return (
    <div className="min-h-screen bg-cover bg-center">
      <Navbar />
      <title>View Designs</title>
      <div className="flex flex-col md:flex-row items-center justify-center p-10 gap-8">
        {/* Left Section*/}
        <div className="md:w-3/4 border-3 p-6 flex items-center justify-center text-gray-600 cursor-pointer bg-white rounded-lg transition-all w-full">
          {/* image grid */}
          <div className="grid grid-cols-3 gap-4 w-full">
            <img src="src\assets\samples\2f2ba762c9db4434b7df1ce426e0758c.jpg" alt="Design 1" className="object-cover w-full h-auto max-h-80 rounded-lg" />
            <img src="src\assets\samples\05ca058f615842878768b567bc24271d.jpg" alt="Design 2" className="object-cover w-full h-auto max-h-80 rounded-lg" />
            <img src="src\assets\samples\7fffd3daccce43008a92674b0e265cf1.jpg" alt="Design 3" className="object-cover w-full h-auto max-h-80 rounded-lg" />
          </div>
        </div>

        {/* Right Section - Text, Color Pickers, Dropdown, and Buttons */}
        <div className="md:w-1/4 text-center md:text-left">
          <h2 className="text-2xl font-bold text-gray-900">Your new designs</h2>
          <p className="text-gray-900 mt-4">
            Here are your generated batik designs. If you want different results, click on New Designs and choose another generator. 
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
            >
              Download
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ViewDesigns
