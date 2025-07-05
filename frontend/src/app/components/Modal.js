"use client";
import BigBlueButton from "./BigBlueButton";

export default function Modal({ children, onClose }) {
  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-25 overflow-y-auto h-full w-full flex items-center justify-center z-50" 
         style={{ backgroundColor: 'rgba(75, 85, 99, 0.55)' }}>
      <div className="p-8 border w-96 shadow-lg rounded-md bg-white">
        <div className="text-center text-black">
          {children}
          <div className="flex justify-center mt-4">
            <BigBlueButton onClick={onClose}>
              Close
            </BigBlueButton>
          </div>
        </div>
      </div>
    </div>
  );
}
