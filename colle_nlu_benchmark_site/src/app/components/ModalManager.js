'use client';

import { useSearchParams } from "next/navigation"
import Modal from "./Modal"
import SubmitForm from "./SubmitForm";

export default function ModalManager(){
    const submitModal = useSearchParams().get("show") === "submit"
    return(
        <>
        {submitModal && <Modal><SubmitForm></SubmitForm></Modal>}
        </>
    );

}
