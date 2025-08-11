import { useDropzone } from "react-dropzone";
import { UploadCloud } from "lucide-react";

export default function UploadDropzone({ onFileSelect, file }) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: (acceptedFiles) => onFileSelect(acceptedFiles[0]),
    accept: { "application/pdf": [".pdf"], "text/csv": [".csv"] },
    multiple: false,
  });

  return (
    <div
      {...getRootProps()}
      className={`p-6 border-2 border-dashed rounded-xl text-center cursor-pointer ${
        isDragActive ? "bg-blue-100" : "bg-white"
      }`}
    >
      <input {...getInputProps()} />
      <UploadCloud className="mx-auto mb-2 text-gray-500" size={32} />
      <p className="text-gray-700">
        {file ? file.name : "Drag & drop PDF or CSV here or click to browse"}
      </p>
    </div>
  );
}
