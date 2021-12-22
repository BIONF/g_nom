-- MySQL Script generated by MySQL Workbench
-- Mon Dec 20 09:54:21 2021
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema gnom_db
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema gnom_db
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `gnom_db` ;
USE `gnom_db` ;

-- -----------------------------------------------------
-- Table `gnom_db`.`taxa`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `gnom_db`.`taxa` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `ncbiTaxonID` INT NOT NULL,
  `parentNcbiTaxonID` INT NOT NULL,
  `scientificName` VARCHAR(400) NOT NULL,
  `taxonRank` VARCHAR(100) NOT NULL,
  `imageStatus` TINYINT(1) NOT NULL DEFAULT 0,
  `lastUpdatedBy` INT NOT NULL,
  `lastUpdatedOn` TIMESTAMP NOT NULL,
  `commonName` VARCHAR(400) NULL DEFAULT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `gnom_db`.`taxaGeneralInfo`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `gnom_db`.`taxaGeneralInfo` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `taxonID` INT NOT NULL,
  `generalInfoLabel` VARCHAR(50) NOT NULL,
  `generalInfoDescription` VARCHAR(500) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `taxonRefGeneralInfo_idx` (`taxonID` ASC) VISIBLE,
  CONSTRAINT `taxaRefGeneralInfo`
    FOREIGN KEY (`taxonID`)
    REFERENCES `gnom_db`.`taxa` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `gnom_db`.`assemblies`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `gnom_db`.`assemblies` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `taxonID` INT NOT NULL,
  `name` VARCHAR(400) NOT NULL,
  `path` VARCHAR(400) NOT NULL,
  `addedBy` INT NOT NULL,
  `addedOn` TIMESTAMP NOT NULL,
  `lastUpdatedBy` INT NOT NULL,
  `lastUpdatedOn` TIMESTAMP NOT NULL,
  `numberOfSequences` INT NOT NULL,
  `sequenceType` VARCHAR(10) NOT NULL,
  `cumulativeSequenceLength` BIGINT NOT NULL,
  `n50` BIGINT NOT NULL,
  `n90` BIGINT NOT NULL,
  `shortestSequence` BIGINT NOT NULL,
  `largestSequence` BIGINT NOT NULL,
  `meanSequence` BIGINT NOT NULL,
  `medianSequence` BIGINT NOT NULL,
  `gcPercent` FLOAT NOT NULL,
  `gcPercentMasked` FLOAT NOT NULL,
  `lengthDistributionString` JSON NOT NULL,
  `charCountString` JSON NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `assemblyName_UNIQUE` (`name` ASC) VISIBLE,
  INDEX `assemblyIDtaxonID_idx` (`taxonID` ASC) VISIBLE,
  CONSTRAINT `assemblyIDtaxonID`
    FOREIGN KEY (`taxonID`)
    REFERENCES `gnom_db`.`taxa` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `gnom_db`.`assembliesGeneralInfo`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `gnom_db`.`assembliesGeneralInfo` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `assemblyID` INT NOT NULL,
  `generalInfoLabel` VARCHAR(50) NOT NULL,
  `generalInfoDescription` VARCHAR(500) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `assemblyIDassemblyGeneralInfo_idx` (`assemblyID` ASC) VISIBLE,
  CONSTRAINT `AssembliesGeneralInfoIDAssemblyID`
    FOREIGN KEY (`assemblyID`)
    REFERENCES `gnom_db`.`assemblies` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `gnom_db`.`genomicAnnotations`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `gnom_db`.`genomicAnnotations` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `assemblyID` INT NOT NULL,
  `name` VARCHAR(400) NOT NULL,
  `path` VARCHAR(400) NOT NULL,
  `addedBy` INT NOT NULL,
  `addedOn` TIMESTAMP NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `assemblyAnnotationID_idx` (`assemblyID` ASC) VISIBLE,
  CONSTRAINT `genomicAnnotationIDAssemblyID`
    FOREIGN KEY (`assemblyID`)
    REFERENCES `gnom_db`.`assemblies` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `gnom_db`.`genomicAnnotationsGeneralInfo`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `gnom_db`.`genomicAnnotationsGeneralInfo` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `annotationID` INT NOT NULL,
  `generalInfoLabel` VARCHAR(50) NOT NULL,
  `generalInfoDescription` VARCHAR(500) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `assemblyIDassemblyGeneralInfo_idx` (`annotationID` ASC) VISIBLE,
  CONSTRAINT `genomicAnnotationsGeneralInfoIDgenomicAnnotationID`
    FOREIGN KEY (`annotationID`)
    REFERENCES `gnom_db`.`genomicAnnotations` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `gnom_db`.`references`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `gnom_db`.`references` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `taxonID` INT NOT NULL,
  `path` VARCHAR(400) NOT NULL,
  `referenceSource` VARCHAR(400) NOT NULL,
  `addedBy` INT NOT NULL,
  `addedOn` TIMESTAMP NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `referenceTaxaID_idx` (`taxonID` ASC) VISIBLE,
  CONSTRAINT `referenceTaxaID`
    FOREIGN KEY (`taxonID`)
    REFERENCES `gnom_db`.`taxa` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `gnom_db`.`analyses`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `gnom_db`.`analyses` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `assemblyID` INT NOT NULL,
  `name` VARCHAR(400) NOT NULL,
  `path` VARCHAR(400) NOT NULL,
  `type` VARCHAR(50) NOT NULL,
  `addedBy` INT NOT NULL,
  `addedOn` TIMESTAMP NOT NULL,
  `additionalFilesPath` VARCHAR(400) NULL,
  PRIMARY KEY (`id`),
  INDEX `assemblyAnalysisID_idx` (`assemblyID` ASC) VISIBLE,
  CONSTRAINT `AnalysisIDAssemblyID`
    FOREIGN KEY (`assemblyID`)
    REFERENCES `gnom_db`.`assemblies` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `gnom_db`.`analysesBusco`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `gnom_db`.`analysesBusco` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `analysisID` INT NOT NULL,
  `completeSingle` INT NOT NULL,
  `completeDuplicated` INT NOT NULL,
  `fragmented` INT NOT NULL,
  `missing` INT NOT NULL,
  `total` INT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `analysisID_UNIQUE` (`analysisID` ASC) VISIBLE,
  CONSTRAINT `BuscoIDAnalysisID`
    FOREIGN KEY (`analysisID`)
    REFERENCES `gnom_db`.`analyses` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `gnom_db`.`analysisGeneralInfo`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `gnom_db`.`analysisGeneralInfo` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `analysisID` INT NOT NULL,
  `generalInfoLabel` VARCHAR(50) NOT NULL,
  `generalInfoDescription` VARCHAR(500) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `analysisIDGeneralInfo_idx` (`analysisID` ASC) VISIBLE,
  CONSTRAINT `AnalysisGeneralInfoIDAnalysisID`
    FOREIGN KEY (`analysisID`)
    REFERENCES `gnom_db`.`analyses` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `gnom_db`.`analysesFcat`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `gnom_db`.`analysesFcat` (
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
  CONSTRAINT `FcatIDAnalysisID`
    FOREIGN KEY (`analysisID`)
    REFERENCES `gnom_db`.`analyses` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `gnom_db`.`mappings`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `gnom_db`.`mappings` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `assemblyID` INT NOT NULL,
  `name` VARCHAR(400) NOT NULL,
  `path` VARCHAR(400) NOT NULL,
  `addedBy` INT NOT NULL,
  `addedOn` TIMESTAMP NOT NULL,
  `additionalFilesPath` VARCHAR(400) NULL,
  PRIMARY KEY (`id`),
  INDEX `assemblyIDMapping_idx` (`assemblyID` ASC) VISIBLE,
  CONSTRAINT `MappingIDAssemblyID`
    FOREIGN KEY (`assemblyID`)
    REFERENCES `gnom_db`.`assemblies` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `gnom_db`.`mappingsGeneralInfo`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `gnom_db`.`mappingsGeneralInfo` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `mappingID` INT NOT NULL,
  `generalInfoLabel` VARCHAR(50) NOT NULL,
  `generalInfoDescription` VARCHAR(500) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `assemblyIDassemblyGeneralInfo_idx` (`mappingID` ASC) VISIBLE,
  CONSTRAINT `MappingGeneralInfoIDMappingID`
    FOREIGN KEY (`mappingID`)
    REFERENCES `gnom_db`.`mappings` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `gnom_db`.`analysesMilts`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `gnom_db`.`analysesMilts` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `analysisID` INT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `analysisID_UNIQUE` (`analysisID` ASC) VISIBLE,
  CONSTRAINT `MiltsIDAnalysisID`
    FOREIGN KEY (`analysisID`)
    REFERENCES `gnom_db`.`analyses` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `gnom_db`.`analysesRepeatmasker`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `gnom_db`.`analysesRepeatmasker` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `analysisID` INT NOT NULL,
  `sines` INT NOT NULL,
  `sines_length` INT NOT NULL,
  `lines` INT NOT NULL,
  `lines_length` INT NOT NULL,
  `ltr_elements` INT NOT NULL,
  `ltr_elements_length` INT NOT NULL,
  `dna_elements` INT NOT NULL,
  `dna_elements_length` INT NOT NULL,
  `unclassified` INT NOT NULL,
  `unclassified_length` INT NOT NULL,
  `rolling_circles` INT NOT NULL,
  `rolling_circles_length` INT NOT NULL,
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
  CONSTRAINT `RepeatmaskerIDAnalysisID`
    FOREIGN KEY (`analysisID`)
    REFERENCES `gnom_db`.`analyses` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `gnom_db`.`assembliesSequences`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `gnom_db`.`assembliesSequences` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `assemblyID` INT NOT NULL,
  `header` VARCHAR(200) NOT NULL,
  `headerIdx` INT NOT NULL,
  `sequenceLength` INT NOT NULL,
  `gcPercentLocal` FLOAT NOT NULL,
  `gcPercentMaskedLocal` FLOAT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `assemblyStatisticsIDassemblyID_idx` (`assemblyID` ASC) VISIBLE,
  CONSTRAINT `AssembliesSequencesIDAssemblyID`
    FOREIGN KEY (`assemblyID`)
    REFERENCES `gnom_db`.`assemblies` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `gnom_db`.`genomicAnnotationFeatures`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `gnom_db`.`genomicAnnotationFeatures` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `annotationID` INT NOT NULL,
  `seqID` VARCHAR(200) NOT NULL,
  `type` VARCHAR(50) NOT NULL,
  `start` BIGINT NOT NULL,
  `end` BIGINT NOT NULL,
  `attributes` JSON NOT NULL,
  `source` VARCHAR(50) NULL,
  `score` FLOAT NULL,
  `strand` VARCHAR(1) NULL,
  `phase` TINYINT NULL,
  PRIMARY KEY (`id`),
  INDEX `AssembliesStatisticsIDAssemblyID_idx` (`annotationID` ASC) VISIBLE,
  CONSTRAINT `genomicAnnotationSequenceIDAssemblyID`
    FOREIGN KEY (`annotationID`)
    REFERENCES `gnom_db`.`genomicAnnotations` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `gnom_db`.`userGroups`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `gnom_db`.`userGroups` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `name_UNIQUE` (`name` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `gnom_db`.`userGroupRefAssembly`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `gnom_db`.`userGroupRefAssembly` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `assemblyID` INT NOT NULL,
  `groupID` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `groupRefAssemblyID_idx` (`assemblyID` ASC) VISIBLE,
  INDEX `groupRefGroupIDGroup_idx` (`groupID` ASC) VISIBLE,
  CONSTRAINT `groupRefAssemblyID`
    FOREIGN KEY (`assemblyID`)
    REFERENCES `gnom_db`.`assemblies` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  CONSTRAINT `groupRefGroupIDGroup`
    FOREIGN KEY (`groupID`)
    REFERENCES `gnom_db`.`userGroups` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `gnom_db`.`globalStatistics`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `gnom_db`.`globalStatistics` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `statisticsLabel` VARCHAR(50) NOT NULL,
  `statisticsValue` VARCHAR(500) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `gnom_db`.`users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `gnom_db`.`users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(50) NOT NULL,
  `password` VARCHAR(200) NOT NULL,
  `userRole` VARCHAR(20) NOT NULL DEFAULT 'admin',
  `activeToken` VARCHAR(200) NULL DEFAULT NULL,
  `tokenCreationTime` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `username_UNIQUE` (`username` ASC) INVISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `gnom_db`.`bookmarks`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `gnom_db`.`bookmarks` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `userID` INT NOT NULL,
  `assemblyID` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `userIDSubscription_idx` (`userID` ASC) VISIBLE,
  INDEX `bookmarkIDAssemblyID_idx` (`assemblyID` ASC) VISIBLE,
  CONSTRAINT `userIDSubscription`
    FOREIGN KEY (`userID`)
    REFERENCES `gnom_db`.`users` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  CONSTRAINT `bookmarkIDAssemblyID`
    FOREIGN KEY (`assemblyID`)
    REFERENCES `gnom_db`.`assemblies` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `gnom_db`.`userGroupRefUser`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `gnom_db`.`userGroupRefUser` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `userID` INT NOT NULL,
  `groupID` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `userRefUserID_idx` (`userID` ASC) VISIBLE,
  INDEX `userRefGroupIDUser_idx` (`groupID` ASC) VISIBLE,
  CONSTRAINT `userRefUserID`
    FOREIGN KEY (`userID`)
    REFERENCES `gnom_db`.`users` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  CONSTRAINT `userRefGroupIDUser`
    FOREIGN KEY (`groupID`)
    REFERENCES `gnom_db`.`userGroups` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `gnom_db`.`tags`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `gnom_db`.`tags` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `assemblyID` INT NOT NULL,
  `tag` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `tagIDAssemblyID_idx` (`assemblyID` ASC) VISIBLE,
  CONSTRAINT `tagIDAssemblyID`
    FOREIGN KEY (`assemblyID`)
    REFERENCES `gnom_db`.`assemblies` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

-- -----------------------------------------------------
-- Data for table `gnom_db`.`userGroups`
-- -----------------------------------------------------
START TRANSACTION;
USE `gnom_db`;
INSERT INTO `gnom_db`.`userGroups` (`id`, `name`) VALUES (DEFAULT, 'all');

COMMIT;


-- -----------------------------------------------------
-- Data for table `gnom_db`.`users`
-- -----------------------------------------------------
START TRANSACTION;
USE `gnom_db`;
INSERT INTO `gnom_db`.`users` (`id`, `username`, `password`, `userRole`, `activeToken`, `tokenCreationTime`) VALUES (DEFAULT, 'admin', 'd987f042a7945828cc9425c13c1e688abf953efccbf34df492552a05d7bbe934a696501851f16616e5e527627d97f1dde346eb1d62d7f11bf929de7d33e8e3eb', 'admin', NULL, NULL);

COMMIT;


-- -----------------------------------------------------
-- Data for table `gnom_db`.`userGroupRefUser`
-- -----------------------------------------------------
START TRANSACTION;
USE `gnom_db`;
INSERT INTO `gnom_db`.`userGroupRefUser` (`id`, `userID`, `groupID`) VALUES (DEFAULT, 1, 1);

COMMIT;

USE `gnom_db`;

DELIMITER $$
USE `gnom_db`$$
CREATE DEFINER = CURRENT_USER TRIGGER `gnom_db`.`assemblies_AFTER_INSERT` AFTER INSERT ON `assemblies` FOR EACH ROW
BEGIN
	INSERT INTO `gnom_db`.`userGroupRefAssembly` (assemblyID, groupID) VALUES (NEW.id, 1);
END$$


DELIMITER ;
