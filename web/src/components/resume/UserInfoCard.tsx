"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { ResumeType } from "@/lib/types/Resume"
import LabelledInput from "../ui/LabelledInput"
import { useState, useEffect } from "react"
import { cn } from "@/lib/utils"

interface UserInfoCardProps {
    userInfo: Partial<Pick<ResumeType, 'name' | 'email' | 'phone' | 'linkedin' | 'github' | 'website'>>;
    onUpdate: (updates: Partial<ResumeType>) => void;
    className?: string;
    onValidation: (isValid: boolean) => void;
}

export default function UserInfoCard({ userInfo, onUpdate, className, onValidation }: UserInfoCardProps) {
    const [errors, setErrors] = useState<Record<string, string | undefined>>({});

    const validate = (name: string, value: string): string | undefined => {
        if (!value) {
            return undefined;
        }
        switch (name) {
            case 'email':
                if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
                    return "Please enter a valid email.";
                }
                break;
            case 'phone':
                if (value.replace(/\D/g, '').length < 7) {
                    return "Please enter a valid phone number.";
                }
                break;
            case 'website':
            case 'linkedin':
            case 'github':
                if (!/^(https?:\/\/)?([\w\d-]+\.)+\w{2,}(\/.+)*\/?$/.test(value)) {
                    return "Please enter a valid URL.";
                }
                break;
        }
        return undefined;
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        onUpdate({ [name]: value });
        setErrors(prev => ({ ...prev, [name]: validate(name, value) }));
    };

    useEffect(() => {
        const hasErrors = Object.values(errors).some(e => e !== undefined);
        onValidation(!hasErrors);
    }, [errors, onValidation]);

    return (
        <Card className={className}>
            <CardHeader>
                <CardTitle>Personal Information</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <LabelledInput
                        label="Full Name"
                        htmlFor="name"
                        input={<Input id="name" name="name" value={userInfo.name || ""} onChange={handleChange} />}
                    />
                </div>
                <div>
                    <LabelledInput
                        label="Email"
                        htmlFor="email"
                        input={<Input id="email" name="email" value={userInfo.email || ""} onChange={handleChange} className={cn({ "border-red-500 focus-visible:ring-red-500": errors.email })} />}
                    />
                    {errors.email && <p className="text-xs text-red-500 mt-1">{errors.email}</p>}
                </div>
                <div>
                    <LabelledInput
                        label="Phone"
                        htmlFor="phone"
                        input={<Input id="phone" name="phone" value={userInfo.phone || ""} onChange={handleChange} className={cn({ "border-red-500 focus-visible:ring-red-500": errors.phone })} />}
                    />
                    {errors.phone && <p className="text-xs text-red-500 mt-1">{errors.phone}</p>}
                </div>
                <div>
                    <LabelledInput
                        label="LinkedIn"
                        htmlFor="linkedin"
                        input={<Input id="linkedin" name="linkedin" value={userInfo.linkedin || ""} onChange={handleChange} className={cn({ "border-red-500 focus-visible:ring-red-500": errors.linkedin })} />}
                    />
                    {errors.linkedin && <p className="text-xs text-red-500 mt-1">{errors.linkedin}</p>}
                </div>
                <div>
                    <LabelledInput
                        label="GitHub"
                        htmlFor="github"
                        input={<Input id="github" name="github" value={userInfo.github || ""} onChange={handleChange} className={cn({ "border-red-500 focus-visible:ring-red-500": errors.github })} />}
                    />
                    {errors.github && <p className="text-xs text-red-500 mt-1">{errors.github}</p>}
                </div>
                <div>
                    <LabelledInput
                        label="Website"
                        htmlFor="website"
                        input={<Input id="website" name="website" value={userInfo.website || ""} onChange={handleChange} className={cn({ "border-red-500 focus-visible:ring-red-500": errors.website })} />}
                    />
                    {errors.website && <p className="text-xs text-red-500 mt-1">{errors.website}</p>}
                </div>
            </CardContent>
        </Card>
    )
}
