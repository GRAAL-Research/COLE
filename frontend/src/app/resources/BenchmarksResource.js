const BASE_PATH = " http://127.0.0.1:8000"


const send_results = async (email, labels) => {
    let path = `${BASE_PATH}/submit`;
    if(!email||!labels){
        alert("email and results must be present")
        return
    }
    const formData = new FormData()
    formData.append("email",email)
    formData.append("labels",labels)
    console.log(email)
    console.log(labels)
 try {
    const response = await fetch(path, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
        console.log(response)
      throw new Error("Failed to submit");

    }
    const result = await response.json();
    console.log("Server response:", result);
    alert("Submission successful!");
  } catch (err) {
    console.error("Error submitting results:", err);
    alert("There was a problem with the submission.");
  }
}

export {send_results}