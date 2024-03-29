# Load libraries
library(lattice)
library(reshape2)
library(colorRamps)

# Set Working directory
dir.create("3D_Habitat_suitability")
setwd("3D_Habitat_suitability")

# Load Data
HS_dir <- "path/to/fuzzy/output_file/"
HS_results_gradient_df <- read.csv(paste(HS_dir,"output_file.txt",sep=""))
HS_results_gradient_df <- HS_results_gradient_df[,!colnames(HS_results_gradient_df) %in% c("east","north","cat")]

HS_results_gradient_df_melt <- melt(HS_results_gradient_df,
                                    id.vars=c("Depth","Velocity"),
                                    value.name="Habitat_suitability",
                                    variable.name="Species")

# Create dataframe for selected species
HS_species_df <- HS_results_gradient_df_melt[HS_results_gradient_df_melt$Species %in% c("Rutiilus_ad","Rutiilus_juv"),]
HS_species_df$Species <- factor(HS_species_df$Species, 
                                     levels=c("Rutiilus_ad","Rutiilus_juv"), 
                                     labels=c("R. rutilus (adult)","R. rutilus (juvenile)"))

# Define color ramp
myCol=colorRampPalette(c("red","yellow","green"))(100)

# 3D plots
pdf(file="Habitat_suitability_Rutiilus_ad.pdf", width=8, height=8,bg="white")
for (i in seq(0, 350 ,5)){
  print(wireframe(Habitat_suitability ~ Depth * Velocity | Species, 
                  data = HS_species_df,
                  aspect = c(1, 1),
                  col.regions=myCol,
                  colorkey = TRUE,
                  drape = TRUE,
                  scales = list(arrows = TRUE,
                                x = list(at = c(0, 0.5, 1, 1.5)),
                                y = list(at = c(0, 0.5, 1))),
                  #xlim=c(1.2,0),
                  xlab=list("d [m] "),
                  ylab=list("v [m/s]"),
                  zlab=list("HS"),
                  par.settings = list(strip.background=list(col="lightgrey")),
                  lwd=0.1,
                  screen = list(z = i, x = -60))
  )    
}
dev.off()

# convert pdf to gif using ImageMagick
system("convert -delay 40 *.pdf Habitat_suitability_Rutiilus_3D.gif")
# cleaning up
file.remove(list.files(pattern=".pdf"))

