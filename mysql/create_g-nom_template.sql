-- MySQL Script generated by MySQL Workbench
-- Mon Jul 26 20:48:43 2021
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema g-nom_template
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema g-nom_template
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `g-nom_template` DEFAULT CHARACTER SET utf8 ;
USE `g-nom_template` ;

-- -----------------------------------------------------
-- Table `g-nom_template`.`taxon`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `g-nom_template`.`taxon` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `ncbiTaxonID` INT NOT NULL,
  `scientificName` VARCHAR(400) NOT NULL,
  `imageStatus` TINYINT(1) NOT NULL DEFAULT 0,
  `lastUpdatedBy` INT NOT NULL,
  `lastUpdatedOn` TIMESTAMP NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `g-nom_template`.`assembly`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `g-nom_template`.`assembly` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `taxonID` INT NOT NULL,
  `name` VARCHAR(400) NOT NULL,
  `path` VARCHAR(400) NOT NULL,
  `addedBy` INT NOT NULL,
  `addedOn` TIMESTAMP NOT NULL,
  `lastUpdatedBy` INT NOT NULL,
  `lastUpdatedOn` TIMESTAMP NOT NULL,
  `additionalFilesPath` VARCHAR(400) NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `assemblyName_UNIQUE` (`name` ASC) VISIBLE,
  INDEX `taxonID_idx` (`taxonID` ASC) VISIBLE,
  CONSTRAINT `taxonID`
    FOREIGN KEY (`taxonID`)
    REFERENCES `g-nom_template`.`taxon` (`id`)
    ON DELETE NO ACTION
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `g-nom_template`.`user`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `g-nom_template`.`user` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(50) NOT NULL,
  `password` VARCHAR(200) NOT NULL,
  `role` VARCHAR(20) NOT NULL DEFAULT 'admin',
  PRIMARY KEY (`id`),
  UNIQUE INDEX `username_UNIQUE` (`username` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `g-nom_template`.`analysis`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `g-nom_template`.`analysis` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `assemblyID` INT NOT NULL,
  `name` VARCHAR(400) NOT NULL,
  `type` VARCHAR(50) NOT NULL,
  `path` VARCHAR(400) NOT NULL,
  `addedBy` INT NOT NULL,
  `addedOn` TIMESTAMP NOT NULL,
  `additionalFilesPath` VARCHAR(400) NULL,
  PRIMARY KEY (`id`),
  INDEX `assemblyAnalysisID_idx` (`assemblyID` ASC) VISIBLE,
  CONSTRAINT `assemblyAnalysisID`
    FOREIGN KEY (`assemblyID`)
    REFERENCES `g-nom_template`.`assembly` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `g-nom_template`.`busco`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `g-nom_template`.`busco` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `analysisID` INT NOT NULL,
  `completeSingle` INT NOT NULL,
  `completeDuplicated` INT NOT NULL,
  `fragmented` INT NOT NULL,
  `missing` INT NOT NULL,
  `total` INT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `analysisID_UNIQUE` (`analysisID` ASC) VISIBLE,
  CONSTRAINT `analysisBuscoID`
    FOREIGN KEY (`analysisID`)
    REFERENCES `g-nom_template`.`analysis` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `g-nom_template`.`milts`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `g-nom_template`.`milts` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `analysisID` INT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `analysisID_UNIQUE` (`analysisID` ASC) VISIBLE,
  CONSTRAINT `analysisMiltsID`
    FOREIGN KEY (`analysisID`)
    REFERENCES `g-nom_template`.`analysis` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `g-nom_template`.`taxonGeneralInfo`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `g-nom_template`.`taxonGeneralInfo` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `taxonID` INT NOT NULL,
  `generalInfoLabel` VARCHAR(400) NOT NULL,
  `generalInfoDescription` VARCHAR(2000) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `taxonIDgeneralInfo_idx` (`taxonID` ASC) VISIBLE,
  CONSTRAINT `taxonIDgeneralInfo`
    FOREIGN KEY (`taxonID`)
    REFERENCES `g-nom_template`.`taxon` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `g-nom_template`.`fcat`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `g-nom_template`.`fcat` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `analysisID` INT NOT NULL,
  `m1_similar` INT NOT NULL,
  `m1_dissimilar` INT NOT NULL,
  `m1_duplicated` INT NOT NULL,
  `m1_missing` INT NOT NULL,
  `m1_ignored` INT NOT NULL,
  `m2_similar` INT NOT NULL,
  `m2_dissimilar` INT NOT NULL,
  `m2_duplicated` INT NOT NULL,
  `m2_missing` INT NOT NULL,
  `m2_ignored` INT NOT NULL,
  `m3_similar` INT NOT NULL,
  `m3_dissimilar` INT NOT NULL,
  `m3_duplicated` INT NOT NULL,
  `m3_missing` INT NOT NULL,
  `m3_ignored` INT NOT NULL,
  `m4_similar` INT NOT NULL,
  `m4_dissimilar` INT NOT NULL,
  `m4_duplicated` INT NOT NULL,
  `m4_missing` INT NOT NULL,
  `m4_ignored` INT NOT NULL,
  `total` INT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `analysisID_UNIQUE` (`analysisID` ASC) VISIBLE,
  CONSTRAINT `analysisFcatID`
    FOREIGN KEY (`analysisID`)
    REFERENCES `g-nom_template`.`analysis` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `g-nom_template`.`repeatmasker`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `g-nom_template`.`repeatmasker` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `analysisID` INT NOT NULL,
  `retroelements` INT NOT NULL,
  `retroelements_length` INT NOT NULL,
  `dna_transposons` INT NOT NULL,
  `dna_transposons_length` INT NOT NULL,
  `rolling_circles` INT NOT NULL,
  `rolling_circles_length` INT NOT NULL,
  `unclassified` INT NOT NULL,
  `unclassified_length` INT NOT NULL,
  `small_rna` INT NOT NULL,
  `small_rna_length` INT NOT NULL,
  `satellites` INT NOT NULL,
  `satellites_length` INT NOT NULL,
  `simple_repeats` INT NOT NULL,
  `simple_repeats_length` INT NOT NULL,
  `low_complexity` INT NOT NULL,
  `low_complexity_length` INT NOT NULL,
  `total_non_repetitive_length` INT NOT NULL,
  `total_repetitive_length` INT NOT NULL,
  `numberN` INT NOT NULL,
  `percentN` FLOAT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `analysisID_UNIQUE` (`analysisID` ASC) VISIBLE,
  CONSTRAINT `analysisRepeatmaskerID`
    FOREIGN KEY (`analysisID`)
    REFERENCES `g-nom_template`.`analysis` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `g-nom_template`.`annotation`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `g-nom_template`.`annotation` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `assemblyID` INT NOT NULL,
  `name` VARCHAR(400) NOT NULL,
  `path` VARCHAR(400) NOT NULL,
  `addedBy` INT NOT NULL,
  `addedOn` TIMESTAMP NOT NULL,
  `additionalFilesPath` VARCHAR(400) NULL,
  PRIMARY KEY (`id`),
  INDEX `assemblyAnnotationID_idx` (`assemblyID` ASC) VISIBLE,
  CONSTRAINT `assemblyAnnotationID`
    FOREIGN KEY (`assemblyID`)
    REFERENCES `g-nom_template`.`assembly` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `g-nom_template`.`bookmark`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `g-nom_template`.`bookmark` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `userID` INT NOT NULL,
  `assemblyID` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `userIDSubscription_idx` (`userID` ASC) VISIBLE,
  INDEX `assemblyIDSubscription_idx` (`assemblyID` ASC) VISIBLE,
  CONSTRAINT `userIDSubscription`
    FOREIGN KEY (`userID`)
    REFERENCES `g-nom_template`.`user` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  CONSTRAINT `assemblyIDSubscription`
    FOREIGN KEY (`assemblyID`)
    REFERENCES `g-nom_template`.`assembly` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `g-nom_template`.`proteins`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `g-nom_template`.`proteins` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `annotationID` INT NOT NULL,
  `path` VARCHAR(400) NOT NULL,
  `additionalFilesPath` VARCHAR(400) NULL,
  PRIMARY KEY (`id`),
  INDEX `annotationIDproteins_idx` (`annotationID` ASC) VISIBLE,
  CONSTRAINT `annotationIDproteins`
    FOREIGN KEY (`annotationID`)
    REFERENCES `g-nom_template`.`annotation` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `g-nom_template`.`assemblyGeneralInfo`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `g-nom_template`.`assemblyGeneralInfo` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `assemblyID` INT NOT NULL,
  `generalInfoLabel` VARCHAR(400) NOT NULL,
  `generalInfoDescription` VARCHAR(400) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `assemblyIDassemblyGeneralInfo_idx` (`assemblyID` ASC) VISIBLE,
  CONSTRAINT `assemblyIDassemblyGeneralInfo`
    FOREIGN KEY (`assemblyID`)
    REFERENCES `g-nom_template`.`assembly` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `g-nom_template`.`proteinFeatures`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `g-nom_template`.`proteinFeatures` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `proteinsID` INT NOT NULL,
  `path` VARCHAR(400) NOT NULL,
  `additionalFilesPath` VARCHAR(400) NULL,
  PRIMARY KEY (`id`),
  INDEX `proteinsIDfeatures_idx` (`proteinsID` ASC) VISIBLE,
  CONSTRAINT `proteinsIDfeatures`
    FOREIGN KEY (`proteinsID`)
    REFERENCES `g-nom_template`.`proteins` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `g-nom_template`.`analysisGeneralInfo`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `g-nom_template`.`analysisGeneralInfo` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `analysisID` INT NOT NULL,
  `generalInfoLabel` VARCHAR(400) NOT NULL,
  `generalInfoDescription` VARCHAR(2000) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `analysisIDGeneralInfo_idx` (`analysisID` ASC) VISIBLE,
  CONSTRAINT `analysisIDGeneralInfo`
    FOREIGN KEY (`analysisID`)
    REFERENCES `g-nom_template`.`analysis` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `g-nom_template`.`mapping`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `g-nom_template`.`mapping` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `assemblyID` INT NOT NULL,
  `name` VARCHAR(400) NOT NULL,
  `path` VARCHAR(400) NOT NULL,
  `addedBy` INT NOT NULL,
  `addedOn` TIMESTAMP NOT NULL,
  `additionalFilesPath` VARCHAR(400) NULL,
  PRIMARY KEY (`id`),
  INDEX `assemblyIDMapping_idx` (`assemblyID` ASC) VISIBLE,
  CONSTRAINT `assemblyIDMapping`
    FOREIGN KEY (`assemblyID`)
    REFERENCES `g-nom_template`.`assembly` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `g-nom_template`.`reference`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `g-nom_template`.`reference` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `taxonID` INT NOT NULL,
  `name` VARCHAR(400) NOT NULL,
  `path` VARCHAR(400) NOT NULL,
  `addedBy` INT NOT NULL,
  `addedOn` TIMESTAMP NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `taxonIDReference_idx` (`taxonID` ASC) VISIBLE,
  CONSTRAINT `taxonIDReference`
    FOREIGN KEY (`taxonID`)
    REFERENCES `g-nom_template`.`taxon` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `g-nom_template`.`assemblyStatistics`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `g-nom_template`.`assemblyStatistics` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `assemblyID` INT NOT NULL,
  `numberOfSequences` INT NOT NULL,
  `cumulativeSequenceLength` INT NOT NULL,
  `n50` INT NOT NULL,
  `n90` INT NOT NULL,
  `largestSequence` INT NOT NULL,
  `gcPercent` FLOAT NOT NULL,
  `gcPercentMasked` FLOAT NOT NULL,
  `softmaskedBases` INT NOT NULL,
  `hardmaskedBases` INT NOT NULL,
  `sequencesLarger1000` INT NOT NULL,
  `cumulativeSequenceLengthSequencesLarger1000` INT NOT NULL,
  `sequencesLarger2500` INT NOT NULL,
  `cumulativeSequenceLengthSequencesLarger2500` INT NOT NULL,
  `sequencesLarger5000` INT NOT NULL,
  `cumulativeSequenceLengthSequencesLarger5000` INT NOT NULL,
  `sequencesLarger10000` INT NOT NULL,
  `cumulativeSequenceLengthSequencesLarger10000` INT NOT NULL,
  `sequencesLarger25000` INT NOT NULL,
  `cumulativeSequenceLengthSequencesLarger25000` INT NOT NULL,
  `sequencesLarger50000` INT NOT NULL,
  `cumulativeSequenceLengthSequencesLarger50000` INT NOT NULL,
  `sequencesLarger100000` INT NOT NULL,
  `cumulativeSequenceLengthSequencesLarger100000` INT NOT NULL,
  `sequencesLarger250000` INT NOT NULL,
  `cumulativeSequenceLengthSequencesLarger250000` INT NOT NULL,
  `sequencesLarger500000` INT NOT NULL,
  `cumulativeSequenceLengthSequencesLarger500000` INT NOT NULL,
  `sequencesLarger1000000` INT NOT NULL,
  `cumulativeSequenceLengthSequencesLarger1000000` INT NOT NULL,
  `sequencesLarger2500000` INT NOT NULL,
  `cumulativeSequenceLengthSequencesLarger2500000` INT NOT NULL,
  `sequencesLarger5000000` INT NOT NULL,
  `cumulativeSequenceLengthSequencesLarger5000000` INT NOT NULL,
  `sequencesLarger10000000` INT NOT NULL,
  `cumulativeSequenceLengthSequencesLarger10000000` INT NOT NULL,
  `sequencesLarger25000000` INT NOT NULL,
  `cumulativeSequenceLengthSequencesLarger25000000` INT NOT NULL,
  `sequencesLarger50000000` INT NOT NULL,
  `cumulativeSequenceLengthSequencesLarger50000000` INT NOT NULL,
  `types` VARCHAR(50) NOT NULL,
  `maskings` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `assemblyStatisticsIDassemblyID_idx` (`assemblyID` ASC) VISIBLE,
  CONSTRAINT `assemblyStatisticsIDassemblyID`
    FOREIGN KEY (`assemblyID`)
    REFERENCES `g-nom_template`.`assembly` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

-- -----------------------------------------------------
-- Data for table `g-nom_template`.`user`
-- -----------------------------------------------------
START TRANSACTION;
USE `g-nom_template`;
INSERT INTO `g-nom_template`.`user` (`id`, `username`, `password`, `role`) VALUES (DEFAULT, 'admin', 'd987f042a7945828cc9425c13c1e688abf953efccbf34df492552a05d7bbe934a696501851f16616e5e527627d97f1dde346eb1d62d7f11bf929de7d33e8e3eb', 'admin');

COMMIT;

