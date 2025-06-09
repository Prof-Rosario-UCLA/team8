interface User {
    id: string;
    name: string;
    email: string;
    profile_picture: string;
    phone: string | null;
    linkedin: string | null;
    github: string | null;
    website: string | null;
}

export type { User };