package funkin.modding;

import haxe.Json;
import haxe.io.Path;
import sys.FileSystem;
import sys.io.File;
import funkin.util.FileUtil;

/**
 * Second mod loader for PE-style mods.
 *
 * PE mods live in a separate `mods_pe/` folder and use `pack.json` metadata
 * (Psych Engine style). They contain no Lua scripts - only chart data, audio
 * and images - so they are adapted at startup into standard Polymod mods:
 *
 *   mods_pe/<mod>/pack.json
 *     -> mods/_pe_<mod>/  (_polymod_meta.json generated)
 *        images/...       copied as-is (paths match the game's assets layout)
 *        songs/...        copied as-is (game loads audio from assets/songs/)
 *        data/songs/<s>/<s>.json  converted to official <s>-chart.json
 *                                + generated <s>-metadata.json
 *
 * Once adapted, the official Polymod loader picks them up like any other mod.
 */
class PEModHandler
{
  /** Folder where PE mods are placed. */
  public static final PE_MOD_FOLDER:String = 'mods_pe';

  /** Prefix used for adapted mod folders inside the official mod root. */
  public static final ADAPT_PREFIX:String = '_pe_';

  /**
   * Scans `mods_pe/` and adapts every PE mod (identified by a pack.json)
   * into the official mod root so Polymod can load them.
   * Safe to call multiple times: already-adapted mods are skipped.
   */
  public static function loadAllPEMods():Void
  {
    #if sys
    if (!FileSystem.exists(PE_MOD_FOLDER)) return;

    var entries:Array<String> = FileSystem.readDirectory(PE_MOD_FOLDER);
    for (entry in entries)
    {
      var modPath:String = Path.join([PE_MOD_FOLDER, entry]);
      if (!FileSystem.isDirectory(modPath)) continue;

      var packPath:String = Path.join([modPath, 'pack.json']);
      if (!FileSystem.exists(packPath)) continue;

      try
      {
        adaptPEMod(entry, modPath, packPath);
      }
      catch (e:Dynamic)
      {
        trace('PEModHandler: failed to adapt PE mod "$entry": $e');
      }
    }
    #end
  }

  static function adaptPEMod(dirName:String, modPath:String, packPath:String):Void
  {
    var pack:Dynamic = Json.parse(File.getContent(packPath));
    var title:String = Reflect.field(pack, 'name');
    if (title == null || title == '') title = dirName;

    var targetDir:String = Path.join([PolymodHandler.MOD_FOLDER, ADAPT_PREFIX + sanitize(dirName)]);
    var metaPath:String = Path.join([targetDir, '_polymod_meta.json']);
    if (FileSystem.exists(metaPath)) return; // already adapted

    FileUtil.createDirIfNotExists(targetDir);

    // Generate Polymod metadata from pack.json
    var meta:Dynamic = {
      title: title,
      description: (Reflect.field(pack, 'description') != null) ? Reflect.field(pack, 'description') : '',
      api_version: '3.0.0',
      version: '1.0.0',
      mod_version: '1.0.0',
      skip_scripts: true
    };
    File.saveContent(metaPath, Json.stringify(meta, '\t'));

    // Copy resources (with chart conversion for data/songs)
    var entries:Array<String> = FileSystem.readDirectory(modPath);
    for (entry in entries)
    {
      if (entry == 'pack.json' || entry == '_polymod_meta.json') continue;

      var srcPath:String = Path.join([modPath, entry]);
      var dstPath:String = Path.join([targetDir, entry]);
      if (FileSystem.isDirectory(srcPath))
      {
        if (entry == 'data')
        {
          copyDataFolder(srcPath, dstPath);
        }
        else
        {
          copyDir(srcPath, dstPath);
        }
      }
      else
      {
        copyFileIfNeeded(srcPath, dstPath);
      }
    }

    trace('PEModHandler: adapted PE mod "$dirName" as "$title"');
  }

  /**
   * data/ folder: songs subfolder needs chart conversion, everything else copies as-is.
   */
  static function copyDataFolder(srcDir:String, dstDir:String):Void
  {
    FileUtil.createDirIfNotExists(dstDir);
    var entries:Array<String> = FileSystem.readDirectory(srcDir);
    for (entry in entries)
    {
      var srcPath:String = Path.join([srcDir, entry]);
      var dstPath:String = Path.join([dstDir, entry]);
      if (FileSystem.isDirectory(srcPath))
      {
        if (entry == 'songs')
        {
          copySongsFolder(srcPath, dstPath);
        }
        else
        {
          copyDir(srcPath, dstPath);
        }
      }
      else
      {
        copyFileIfNeeded(srcPath, dstPath);
      }
    }
  }

  /**
   * data/songs/<song>/ : PE chart `<song>.json` -> official `<song>-chart.json` + `<song>-metadata.json`.
   * Other files (audio, subtitles...) copy as-is.
   */
  static function copySongsFolder(srcDir:String, dstDir:String):Void
  {
    FileUtil.createDirIfNotExists(dstDir);
    var entries:Array<String> = FileSystem.readDirectory(srcDir);
    for (entry in entries)
    {
      var srcPath:String = Path.join([srcDir, entry]);
      var dstPath:String = Path.join([dstDir, entry]);
      if (FileSystem.isDirectory(srcPath))
      {
        FileUtil.createDirIfNotExists(dstPath);
        var files:Array<String> = FileSystem.readDirectory(srcPath);
        for (f in files)
        {
          var srcFile:String = Path.join([srcPath, f]);
          var dstFile:String = Path.join([dstPath, f]);
          if (f == '$entry.json')
          {
            // PE chart: convert to official chart + metadata
            var chartDst:String = Path.join([dstPath, '$entry-chart.json']);
            var metaDst:String = Path.join([dstPath, '$entry-metadata.json']);
            if (!FileSystem.exists(chartDst))
            {
              try
              {
                var converted = convertPsychChart(File.getContent(srcFile), entry);
                File.saveContent(chartDst, converted.chartJson);
                File.saveContent(metaDst, converted.metaJson);
                trace('PEModHandler: converted chart "$entry"');
              }
              catch (e:Dynamic)
              {
                trace('PEModHandler: chart conversion failed for "$entry": $e');
              }
            }
          }
          else
          {
            copyFileIfNeeded(srcFile, dstFile);
          }
        }
      }
      else
      {
        copyFileIfNeeded(srcPath, dstPath);
      }
    }
  }

  /**
   * Convert a Psych Engine chart JSON into the official chart + metadata format.
   * Returns the JSON strings to write to `<song>-chart.json` / `<song>-metadata.json`.
   */
  static function convertPsychChart(rawJson:String, songId:String):{chartJson:String, metaJson:String}
  {
    var data:Dynamic = Json.parse(rawJson);
    var song:Dynamic = Reflect.field(data, 'song');
    if (song == null) throw 'no "song" field';

    var bpm:Null<Float> = Reflect.field(song, 'bpm');
    if (bpm == null) bpm = 100;
    var speed:Null<Float> = Reflect.field(song, 'speed');
    if (speed == null) speed = 1.0;

    // Flatten psych's nested section notes into a single note list
    var noteData:Array<Dynamic> = [];
    var sections:Array<Dynamic> = Reflect.field(song, 'notes');
    if (sections != null)
    {
      for (section in sections)
      {
        var sectionTime:Null<Float> = Reflect.field(section, 'strumTime');
        if (sectionTime == null) sectionTime = 0;
        var sectionNotes:Array<Dynamic> = Reflect.field(section, 'notes');
        if (sectionNotes == null) continue;
        for (n in sectionNotes)
        {
          var time:Float = sectionTime + (Reflect.field(n, 'strumTime') ?? 0);
          var lane:Null<Int> = Reflect.field(n, 'lane');
          if (lane == null) lane = 0;
          var len:Null<Float> = Reflect.field(n, 'sustainLength');
          if (len == null) len = 0;
          var kind:Dynamic = Reflect.field(n, 'noteType');
          if (kind == null || kind == '') kind = null;

          noteData.push({t: time, d: lane, l: len, k: kind});
        }
      }
      noteData.sort((a, b) -> a.t - b.t);
    }

    var chart:Dynamic = {
      version: '3.0.0',
      scrollSpeed: {normal: speed},
      events: [],
      notes: {normal: noteData},
      generatedBy: 'PEModHandler'
    };

    var meta:Dynamic = {
      version: '3.0.0',
      songName: songId,
      artist: 'PE Mod',
      charter: 'PE Mod',
      offsets: {},
      playData: {
        songVariations: ['normal'],
        difficulties: ['easy', 'normal', 'hard'],
        characters: {
          player: 'bf',
          girlfriend: 'gf',
          opponent: 'dad',
          altInstrumentals: [],
          opponentVocals: null,
          playerVocals: null
        },
        stage: 'mainStage',
        noteStyle: 'funkin',
        ratings: {}
      },
      generatedBy: 'PEModHandler',
      timeChanges: [{t: 0, b: 0, bpm: bpm, bt: [4, 4, 4, 4]}]
    };

    return {chartJson: Json.stringify(chart), metaJson: Json.stringify(meta)};
  }

  static function sanitize(name:String):String
  {
    return StringTools.replace(name, '/', '_');
  }

  static function copyDir(srcDir:String, dstDir:String):Void
  {
    FileUtil.createDirIfNotExists(dstDir);
    var entries:Array<String> = FileSystem.readDirectory(srcDir);
    for (entry in entries)
    {
      var srcPath:String = Path.join([srcDir, entry]);
      var dstPath:String = Path.join([dstDir, entry]);
      if (FileSystem.isDirectory(srcPath))
      {
        copyDir(srcPath, dstPath);
      }
      else
      {
        copyFileIfNeeded(srcPath, dstPath);
      }
    }
  }

  static function copyFileIfNeeded(srcPath:String, dstPath:String):Void
  {
    if (!FileSystem.exists(dstPath))
    {
      File.saveBytes(dstPath, File.getBytes(srcPath));
    }
  }
}
