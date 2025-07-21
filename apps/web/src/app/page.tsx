"use client";

import { useUser } from "@clerk/clerk-react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import Header from "@/components/Header";
import Benefits from "@/components/home/Benefits";
import Footer from "@/components/home/Footer";
import FooterHero from "@/components/home/FooterHero";
import Hero from "@/components/home/Hero";
import Testimonials from "@/components/home/Testimonials";

export default function Home() {
  const { user, isLoaded } = useUser();
  const router = useRouter();

  useEffect(() => {
    if (isLoaded && user) {
      router.push("/songs");
    }
  }, [isLoaded, user, router]);

  if (!isLoaded) {
    return <div>Loading...</div>;
  }

  if (user) {
    return null; // Will redirect to /songs
  }

  return (
    <main>
      <Header />
      <Hero />
      <Benefits />
      <Testimonials />
      <FooterHero />
      <Footer />
    </main>
  );
}
