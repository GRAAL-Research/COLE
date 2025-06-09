import { useState } from "react";
import UploadButton from "./UploadButton";
import BigBlueButton from "./BigBlueButton";
import {send_results} from "../resources/BenchmarksResource"
import ErrorMessage from "./ErrorMessage";

export default function SubmitForm(){
    const [required_visible,setRequiredVisible] = useState(false)
    const [email,setEmail] = useState("")
    const [file,setFile] = useState(null)

    const submitResults = (email,file) => {
    if(!email||!file){
        showRequired()
    }
    else{
        setRequiredVisible(false)
        send_results(email,file)
    }}

    const showRequired = () =>{
        setRequiredVisible(true)
    }

    return (
    <div className="space-y-6 bg-white rounded-xl shadow-md p-6 w-full max-w-xl mx-auto border border-gray-200">
      
      <h2 className="text-2xl font-semibold text-gray-800 text-center">
        Submit Your Results
      </h2>

      <div className="space-y-2">
        <label htmlFor="email" className="block text-sm font-medium text-gray-700">
          Your Email
        </label>
        <input
          id="email"
          type="email"
          placeholder="your_email@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="border border-gray-300 p-3 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <p className="text-xs text-gray-500">
          We’ll notify you at this address when your results are ready. This process may take some time.
        </p>
      </div>

      <UploadButton uploaded={(file) => { setFile(file); console.log(file); }}>
        Upload Labels
      </UploadButton>

      <p className="text-sm text-gray-600 italic">
        Please ensure your data is properly formatted. Refer to our <a href="/guide" className="text-blue-500 underline">guide</a> for more info.
      </p>

        <ErrorMessage condition={required_visible}>⚠️ Please provide both an email and a file before submitting.</ErrorMessage>
        <BigBlueButton onClick={() => submitResults(email, file)}>
          Submit Your Results
        </BigBlueButton>
      </div>
    
  );
}
