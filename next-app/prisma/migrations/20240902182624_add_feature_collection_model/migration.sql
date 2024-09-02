-- CreateTable
CREATE TABLE "FeatureCollection" (
    "id" SERIAL NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "crs" JSONB,
    "features" JSONB NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "FeatureCollection_pkey" PRIMARY KEY ("id")
);
