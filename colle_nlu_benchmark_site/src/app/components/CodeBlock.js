export default function CodeBlock({children}){
    return (
        <pre className="bg-gray-100 p-4 rounded-md overflow-x-auto text-sm text-gray-800 mt-4">
          <code className="font-mono">
            {children}
          </code>
        </pre>

    );
};