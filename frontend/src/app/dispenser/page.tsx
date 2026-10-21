import React from "react";
import SeedDispenserClientView from "@/components/dispenser/SeedDispenserClientView";

export const metadata = {
  title: "Seed Dispenser Control - AgriBot IoT",
  description: "Real-time Autonomous Seed Delivery Hardware Actuation & Relay Status",
};

/**
 * SEED DISPENSER CONTROL PAGE (/dispenser)
 * Connects directly to the ESP32 Seed Dispenser Web Server over local Wi-Fi.
 */
export default function SeedDispenserPage() {
  return <SeedDispenserClientView />;
}
