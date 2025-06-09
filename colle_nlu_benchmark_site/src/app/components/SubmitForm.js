import { useState } from "react";
import UploadButton from "./UploadButton";
import BigBlueButton from "./BigBlueButton";
import send_results from "../resources/BenchmarksResource"
export default function SubmitForm(){
    const [email,setEmail] = useState("")
    const [file,setFile] = useState(null)
    return(
        <div>
            <div>
                Please enter a email to receive your results when they'll be ready
                <input 
                type="email"
                placeholder="Enter email here"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="border p-2 rounded w-full"
                />
            </div>
            <UploadButton uploaded={(file) => {setFile(file); console.log(file)} }>Submit files</UploadButton>
            <div>Please ensure your data is properly formatted, refer to our guide for more information</div>
            <BigBlueButton onClick={() => submitResults(email,file)}>Submit your results</BigBlueButton>
        </div>

    );
}
const submitResults = (email,file) => {

    send_results(email,file)

}