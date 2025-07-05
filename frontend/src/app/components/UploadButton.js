

import { useState } from "react";
import BigBlueButton from "./BigBlueButton";

export default function UploadButton({children,uploaded}){
      const [file, setFile] = useState(null);

  function handleFileChange(e) {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      uploaded(selectedFile);
    }
  }
return(
    <div>
        <label htmlFor="file_upload">{children}</label>
        <input type="file" id="file_upload" accept=".zip" onChange={handleFileChange}
    className="bg-gray-500 text-white text-base
     font-medium rounded-md shadow-sm hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-300"></input>
    </div>
);

}

const uploadFile = async () => {}