"use client";

import Image from "next/image";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { SparklesIcon, ArrowRightIcon, CookieIcon } from "lucide-react";
import { useEffect, useState } from "react";
import LoadingPage from "@/components/loading/Loading";

/**
 * cookie consent banner that gates site access.
 * uses localStorage to remember the user's choice.
 */
const CookieBanner = () => {
    const [showBanner, setShowBanner] = useState(false);
    const [isMounted, setIsMounted] = useState(false);

    useEffect(() => {
        // This check runs only on the client-side after hydration.
        const consent = localStorage.getItem("cookieConsent");
        if (consent !== "true") {
            setShowBanner(true);
        }
    }, []);

    useEffect(() => {
        if (showBanner) {
            // After the component is shown, wait a moment to trigger the transition
            const timer = setTimeout(() => {
                setIsMounted(true);
            }, 10);
            return () => clearTimeout(timer);
        }
    }, [showBanner]);

    const handleAccept = () => {
        setIsMounted(false);
        setTimeout(() => {
            localStorage.setItem("cookieConsent", "true");
            setShowBanner(false);
        }, 300); // Match transition duration
    };

    const handleDecline = () => {
        // Redirects to Google
        window.location.href = "https://www.google.com";
    };

    if (!showBanner) {
        return null;
    }

    return (
        <div
            data-state={isMounted ? "open" : "closed"}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm transition-opacity duration-300 data-[state=closed]:opacity-0"
        >
            <div
                data-state={isMounted ? "open" : "closed"}
                className="bg-white rounded-lg shadow-2xl max-w-md w-full p-6 text-center transform transition-all duration-300 data-[state=open]:animate-in data-[state=open]:zoom-in-95 data-[state=closed]:animate-out data-[state=closed]:zoom-out-95"
            >
                <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-blue-100">
                    <CookieIcon className="h-6 w-6 text-blue-600" aria-hidden="true" />
                </div>
                <h3 className="mt-4 text-xl font-semibold text-gray-900">Cookie Consent</h3>
                <div className="mt-2">
                    <p className="text-sm text-gray-600">
                        We use essential cookies to ensure our site functions correctly. By clicking &quot;Accept&quot;, you agree to our use of these cookies. If you decline, you will be redirected away from the site.
                    </p>
                </div>
                <div className="mt-6 flex flex-col justify-center gap-4">
                    <Button
                        onClick={handleAccept}
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                    >
                        Accept
                    </Button>
                    <Button
                        onClick={handleDecline}
                        variant="outline"
                        className="w-full"
                    >
                        Decline
                    </Button>
                </div>
            </div>
        </div>
    );
};


export default function Home() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [isUserLoggedIn, setIsUserLoggedIn] = useState(false);

    useEffect(() => {
        fetch("/api/user/me", { credentials: 'include' })
            .then(res => res.ok ? res.json() : null)
            .then(data => {
                setIsUserLoggedIn(data !== null);
            })
            .catch(() => {
                setIsUserLoggedIn(false);
            }).finally(() => {
                setIsLoaded(true);
            });
    }, []);


    if (!isLoaded) {
        return <LoadingPage message="Loading..." />;
    }

    return (
        <>
            <CookieBanner />
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
                                <Button
                                    size="lg"
                                    className="bg-blue-600 hover:bg-blue-700 text-white"
                                    onClick={()=>{
                                        // Give the illusion of an instant redirect
                                        setIsLoaded(false);
                                        window.location.href = "/api/auth/login?next=/resume/dashboard";
                                    }}
                                >
                                    Login
                                </Button>
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
        </>
    );
}
