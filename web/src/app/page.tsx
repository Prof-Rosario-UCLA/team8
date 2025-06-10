"use client";

import Image from "next/image";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { SparklesIcon, ArrowRightIcon } from "lucide-react";
import { useEffect, useState } from "react";
import LoadingPage from "@/components/loading/Loading";

export default function Home() {
    const [isLoading, setIsLoading] = useState(true);
    const [isUserLoggedIn, setIsUserLoggedIn] = useState(false);

    useEffect(() => {
        setIsLoading(true);
        fetch("/api/user/me", { credentials: 'include' })
            .then(res => res.ok ? res.json() : null)
            .then(data => setIsUserLoggedIn(data !== null));
        setIsLoading(false);
    }, []);
    

    if (isLoading) {
        return <LoadingPage message="Loading..." />;
    }
    
    return (
        <main className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
            <section className="w-full max-w-5xl">
                <article className="flex flex-col items-center gap-8 text-center md:flex-row md:gap-12 md:text-left">
                    <div className="flex-1 space-y-6">
                        <div className="flex justify-center md:justify-start">
                            <div className="inline-flex items-center space-x-2 rounded-full bg-blue-100 px-4 py-2">
                                <SparklesIcon className="h-5 w-5 text-blue-600" />
                                <span className="text-sm font-medium text-blue-800">
                                    Professional Resume Builder
                                </span>
                            </div>
                        </div>

                        <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
                            Create Your Perfect{" "}
                            <span className="text-blue-600">Resume</span>
                        </h1>

                        <p className="max-w-2xl text-lg text-gray-600">
                            Build professional resumes with our intuitive editor. Leverage the
                            power of LaTex templates without writing LaTeX, and export to PDF
                            with ease.
                            <br />
                            <span className="text-blue-600 font-bold">
                                Your next job starts here.
                            </span>
                        </p>

                        <div className="flex flex-row gap-4 justify-center md:justify-start">
                            <Link href="/resume/dashboard">
                                <Button
                                    size="lg"
                                    className="bg-blue-600 hover:bg-blue-700 text-white"
                                >
                                    Get Started
                                    <ArrowRightIcon className="ml-2 h-4 w-4" />
                                </Button>
                            </Link>

                            {!isUserLoggedIn && (
                                <Link href="/api/auth/login?next=/">
                                    <Button
                                        size="lg"
                                    className="bg-blue-600 hover:bg-blue-700 text-white"
                                >
                                    Login
                                </Button>
                            </Link>
                            )}

                        </div>
                    </div>
                    <div className="hidden flex-1 md:block">
                        <Image
                            src="/ProlioHeroImage.png"
                            alt="Prolio Hero Image which shows a man thinking up a resume"
                            width={500}
                            height={500}
                            className="rounded-lg shadow-xl"
                        />
                    </div>
                </article>
            </section>
        </main>
    );
}
