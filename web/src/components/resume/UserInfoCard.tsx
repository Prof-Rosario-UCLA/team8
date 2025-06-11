"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { ResumeType } from "@/lib/types/Resume"
import LabelledInput from "../ui/LabelledInput"

interface UserInfoCardProps {
  userInfo: Partial<Pick<ResumeType, 'name' | 'email' | 'phone' | 'linkedin' | 'github' | 'website'>>;
  onUpdate: (updates: Partial<ResumeType>) => void;
  className?: string;
}

export default function UserInfoCard({ userInfo, onUpdate, className }: UserInfoCardProps) {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onUpdate({ [e.target.name]: e.target.value });
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>Personal Information</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <LabelledInput
          label="Full Name"
          htmlFor="name"
          input={<Input id="name" name="name" value={userInfo.name || ""} onChange={handleChange} />}
        />
        <LabelledInput
          label="Email"
          htmlFor="email"
          input={<Input id="email" name="email" value={userInfo.email || ""} onChange={handleChange} />}
        />
        <LabelledInput
          label="Phone"
          htmlFor="phone"
          input={<Input id="phone" name="phone" value={userInfo.phone || ""} onChange={handleChange} />}
        />
        <LabelledInput
          label="LinkedIn"
          htmlFor="linkedin"
          input={<Input id="linkedin" name="linkedin" value={userInfo.linkedin || ""} onChange={handleChange} />}
        />
        <LabelledInput
          label="GitHub"
          htmlFor="github"
          input={<Input id="github" name="github" value={userInfo.github || ""} onChange={handleChange} />}
        />
        <LabelledInput
          label="Website"
          htmlFor="website"
          input={<Input id="website" name="website" value={userInfo.website || ""} onChange={handleChange} />}
        />
      </CardContent>
    </Card>
  )
}
 