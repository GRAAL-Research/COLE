export default function BigBlueButton({children,onClick}){
return(
        <button
             onClick={onClick}
              className="px-4 py-2 bg-blue-500 text-white text-base font-medium rounded-md shadow-sm hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-300"
            >{children}</button>
);

}