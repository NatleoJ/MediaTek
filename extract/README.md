# Extracting from Device Firmware
Instead of extracting from the physical device, it would be more feasible to extract the modem from the phone's firmware/operating system. This process seems to be largely undocumented (on google). From my research, I found that the modem image on Android roms is usually extant in either of the following:
* System image
* Vendor image
* `<Modem name>` image

In general, an Android rom is usually a zip file containing multiple image files that include the boot, system, vendor, and modem images. In Android 9 and 10, some of these images are combined into one called the SUPER image. Most of these image files are in Android Sparse Image Format, and can be "unsparsed" using this: [imjtool](http://newandroidbook.com/tools/imjtool.html). Once extracted, the image files can be mounted on Linux machines, and have its contents accessed.

## Modem
For older roms, simply mounting the system or vendor images will allow access to the /system/etc/firmware folder. The folder will contain the modem image and sometimes the debug symbol file. On newer roms, the modem is found in the MD1IMG image file. This file is not a sparse image, but a single binary that contains multiple partitions (or files). Each partition starts with a partition header, followed by its data and padding. The format of the partition header is shown below. 

```c
typedef union {
    struct {
        unsigned int magic;        /* partition magic = 0x58881688 */
        unsigned int dsize;        /* partition data size (excludes header size) */
        char         name[32];     /* partition name */
        unsigned int maddr;        /* partition memory address */
        unsigned int mode;      /* maddr is counted from the beginning or end of RAM */
        /* extension */
        unsigned int ext_magic;    /* always EXT_MAGIC = 0x58891689 */
        unsigned int hdr_size;     /* header size is 512 bytes currently, but may extend in the future */
        unsigned int hdr_version;  /* see HDR_VERSION */
        unsigned int img_type;     /* please refer to #define beginning with IMG_TYPE_ */
        unsigned int img_list_end; /* end of image list? 0: this image is followed by another image 1: end */
        unsigned int align_size;   /* image size alignment setting in bytes, 16 by default for AES encryption */
        unsigned int dsize_extend; /* high word of image size for 64 bit address support */
        unsigned int maddr_extend; /* high word of image load address in RAM for 64 bit address support */
    } info;
    unsigned char data[PART_HDR_DATA_SIZE]; /* 512 */
} part_hdr_t;
```
# Huawei Y6s 2020 MD1IMG Partitions
* md1rom - modem image
* cert1md - modem image certificate
* cert2md - modem image secondary certificate
* md1dsp - modem dsp image
* cert1 - modem dsp certificate
* cert2 - modem dsp secondary certificate
* md1_filter_SlimLog_DspAllOff
* md1_filter__Default
* md1_filter
* md1_filter_FullLog
* md1_filter_meta
* md1_filter_default_USIR
* md1_filter_PLS_PS_ONLY
* md1_emfilter
* md1_dbginfodsp - modem dsp debug symbols
* md1_dbginfo - modem debug symbols
* md1_mddbmeta
* md1_mddbmetaodb
* md1_mddb
* md1_mdmlayout
* md1_file_map
