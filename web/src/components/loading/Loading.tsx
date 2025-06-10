import LoadingSpinner from "./LoadingSpinner";

export default function LoadingPage({ message }: { message?: string }) {
    return (
        <div className="flex items-center justify-center min-h-screen">
            <div className="text-center">
                <LoadingSpinner message={message} />
            </div>
        </div>
    );
} 
