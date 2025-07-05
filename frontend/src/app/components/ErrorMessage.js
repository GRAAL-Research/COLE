export default function ErrorMessage({children,condition}){
return(
    <div className="pt-2">
        <div className="pt-2 space-y-2">
            {condition && (
        <div className="text-red-600 text-sm font-medium">
            {children}
        </div>
        )}
        </div>
    </div>
);

}