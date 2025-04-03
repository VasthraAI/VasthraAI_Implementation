import React from "react";

const Navbar = () => {
  return (
    <nav className="bg-[#0A1D61] p-4 flex justify-between items-center">
      <div className="flex-1"></div> {/* Empty space to balance alignment */}
      <div className="flex justify-center">
        <img src="src\assets\VasthraAI_white.png" alt="Logo" className="h-12" />
      </div>
      <div className="flex-1 flex justify-end">
        <button className="border border-white text-white px-4 py-1 rounded-lg hover:bg-white hover:text-[#0A1D61] transition">
          Log In
        </button>
      </div>
    </nav>
  );
};

export default Navbar;
