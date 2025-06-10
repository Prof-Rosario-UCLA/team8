export default function LoadingSpinner({ message }: { message?: string }) {
    return (
        <div className="flex flex-col items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto my-4"></div>
            <p className="text-gray-600">{message || "Loading..."}</p>
        </div>
    );
}