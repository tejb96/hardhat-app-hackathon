"use client";

import Image from "next/image";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { UploadCloud, FileText, ShieldCheck } from "lucide-react";
import { motion } from "framer-motion";

export default function HomeMotion() {
  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="max-w-5xl w-full grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
        {/* Left */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="space-y-6"
        >
          <h1 className="text-4xl font-bold tracking-tight">PPE Detector</h1>

          <p className="text-base text-muted-foreground">
            Upload an image to automatically detect personal protective equipment (PPE)
            using a YOLOv8-based computer vision model. The image is analyzed by the API,
            and a detailed PDF report is generated and returned for compliance review.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Card className="rounded-2xl">
              <CardHeader className="pb-2">
                <UploadCloud className="h-6 w-6" />
                <CardTitle className="text-sm">Upload Image</CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-muted-foreground">
                Submit a JPG or PNG image containing workers or equipment.
              </CardContent>
            </Card>

            <Card className="rounded-2xl">
              <CardHeader className="pb-2">
                <ShieldCheck className="h-6 w-6" />
                <CardTitle className="text-sm">Detect PPE</CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-muted-foreground">
                YOLOv8 identifies helmets, vests, gloves, and other PPE.
              </CardContent>
            </Card>

            <Card className="rounded-2xl">
              <CardHeader className="pb-2">
                <FileText className="h-6 w-6" />
                <CardTitle className="text-sm">PDF Report</CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-muted-foreground">
                Receive a generated PDF summarizing detections and results.
              </CardContent>
            </Card>
          </div>

          <Button size="lg" className="rounded-2xl">
            Upload Image
          </Button>
        </motion.div>

        {/* Right */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="flex justify-center"
        >
          <Card className="rounded-2xl shadow-lg w-full max-w-md">
            <CardContent className="p-6">
              <div className="aspect-square relative rounded-xl overflow-hidden bg-muted">
                <Image
                  src="/placeholder.png"
                  alt="PPE detection preview"
                  fill
                  className="object-cover"
                />
              </div>
              <p className="mt-4 text-sm text-muted-foreground text-center">
                Example image processed by the PPE detection pipeline
              </p>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
