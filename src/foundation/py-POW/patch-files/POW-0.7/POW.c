/*****************************************************************************/
/*                                                                           */
/*  Copyright (c) 2001, 2002, Peter Shannon                                  */
/*  All rights reserved.                                                     */
/*                                                                           */
/*  Redistribution and use in source and binary forms, with or without       */
/*  modification, are permitted provided that the following conditions       */
/*  are met:                                                                 */
/*                                                                           */
/*      * Redistributions of source code must retain the above               */
/*        copyright notice, this list of conditions and the following        */
/*        disclaimer.                                                        */
/*                                                                           */
/*      * Redistributions in binary form must reproduce the above            */
/*        copyright notice, this list of conditions and the following        */
/*        disclaimer in the documentation and/or other materials             */
/*        provided with the distribution.                                    */
/*                                                                           */
/*      * The name of the contributors may be used to endorse or promote     */
/*        products derived from this software without specific prior         */
/*        written permission.                                                */
/*                                                                           */
/*  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS      */
/*  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT        */
/*  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS        */
/*  FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS   */
/*  OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,          */
/*  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT         */
/*  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,    */
/*  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY    */
/*  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT      */
/*  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE    */
/*  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.     */
/*                                                                           */
/*****************************************************************************/

#include <Python.h>

#include <openssl/crypto.h>
#include <openssl/rand.h>
#include <openssl/asn1.h>
#include <openssl/x509.h>
#include <openssl/x509v3.h>
#include <openssl/pem.h>
#include <openssl/ssl.h>
#include <openssl/evp.h>
#include <openssl/err.h>
#include <openssl/md5.h>
#include <openssl/md2.h>
#include <openssl/sha.h>
#include <openssl/hmac.h>
#include <openssl/ripemd.h>

#include <time.h>

// semetric ciphers
#define DES_ECB               1
#define DES_EDE               2
#define DES_EDE3              3
#define DES_CFB               4
#define DES_EDE_CFB           5
#define DES_EDE3_CFB          6
#define DES_OFB               7
#define DES_EDE_OFB           8
#define DES_EDE3_OFB          9
#define DES_CBC               10
#define DES_EDE_CBC           11
#define DES_EDE3_CBC          12
#define DESX_CBC              13
#define RC4                   14
#define RC4_40                15
#define IDEA_ECB              16
#define IDEA_CFB              17
#define IDEA_OFB              18
#define IDEA_CBC              19
#define RC2_ECB               20
#define RC2_CBC               21
#define RC2_40_CBC            22
#define RC2_CFB               23
#define RC2_OFB               24
#define BF_ECB                25
#define BF_CBC                26
#define BF_CFB                27
#define BF_OFB                28
#define CAST5_ECB             29
#define CAST5_CBC             30
#define CAST5_CFB             31
#define CAST5_OFB             32
#define RC5_32_12_16_CBC      33
#define RC5_32_12_16_CFB      34
#define RC5_32_12_16_ECB      35
#define RC5_32_12_16_OFB      36

// SSL connection methods
#define SSLV2_SERVER_METHOD   1
#define SSLV2_CLIENT_METHOD   2
#define SSLV2_METHOD          3
#define SSLV3_SERVER_METHOD   4
#define SSLV3_CLIENT_METHOD   5
#define SSLV3_METHOD          6
#define TLSV1_SERVER_METHOD   7
#define TLSV1_CLIENT_METHOD   8
#define TLSV1_METHOD          9
#define SSLV23_SERVER_METHOD  10
#define SSLV23_CLIENT_METHOD  11
#define SSLV23_METHOD         12

// SSL connection states

// PEM encoded data types
#define RSA_PUBLIC_KEY        1 
#define RSA_PRIVATE_KEY       2 
#define DSA_PUBLIC_KEY        3 
#define DSA_PRIVATE_KEY       4 
#define DH_PUBLIC_KEY         5 
#define DH_PRIVATE_KEY        6 
#define X509_CERTIFICATE      7
#define X_X509_CRL            8     //X509_CRL already used by OpenSSL library

// asymmetric ciphers
#define RSA_CIPHER            1
#define DSA_CIPHER            2
#define DH_CIPHER             3
#define NO_DSA
#define NO_DH

// digests
#define MD2_DIGEST            1
#define MD5_DIGEST            2
#define SHA_DIGEST            3
#define SHA1_DIGEST           4
#define RIPEMD160_DIGEST      5

//object format
#define SHORTNAME_FORMAT      1
#define LONGNAME_FORMAT       2

//output format
#define PEM_FORMAT            1
#define DER_FORMAT            2

//object check functions
#define X_X509_Check(op) ((op)->ob_type == &x509type)
#define X_X509_store_Check(op) ((op)->ob_type == &x509_storetype)
#define X_X509_crl_Check(op) ((op)->ob_type == &x509_crltype)
#define X_X509_revoked_Check(op) ((op)->ob_type == &x509_revokedtype)
#define X_asymmetric_Check(op) ((op)->ob_type == &asymmetrictype)
#define X_symmetric_Check(op) ((op)->ob_type == &symmetrictype)
#define X_digest_Check(op) ((op)->ob_type == &digesttype)
#define X_hmac_Check(op) ((op)->ob_type == &hmactype)
#define X_ssl_Check(op) ((op)->ob_type == &ssltype)

static char pow_module__doc__ [] = 
"<moduleDescription>\n"
"   <header>\n"
"      <name>POW</name>\n"
"      <author>Peter Shannon</author>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"	 This third major release of POW addresses the most critical missing\n"
"	 parts of functionality, X509v3 support.  Initially I thought adding\n"
"	 support via the OpenSSL code would be the easiest option but this\n"
"	 proved to be incorrect mainly due to the way I have chosen to handle\n"
"	 the complex data such as <classname>directoryNames</classname> and\n"
"	 <classname>generalNames</classname>.  It is easier in python to\n"
"	 construct complex sets of data using lists and dictionaries than\n"
"	 coordinate large numbers of objects and method calls.  This is no\n"
"	 criticism, it is just extremely easy.  Coding complex data such as the\n"
"	 <classname>certificatePolicies</classname> coding coding routines in C\n"
"	 to handle the data proved laborous and ultimately error prone.\n"
"      </para>\n"
"      <para>\n"
"	 PKIX structures are supported by a few operations on the relevant POW\n"
"	 objects and through a Python library which is modelled on the DER\n"
"	 encoding rules.  Modeling DER does expose some of the complexities of\n"
"	 the ASN1 specifications but avoids coding many assumptions into the\n"
"	 data structures and the interface for the objects.  For an example of\n"
"	 overly complex definitions take a look at the\n"
"	 <classname>Name</classname> object in RFC3280.  It is equally\n"
"	 important that modeling DER in the way leads to a library which is\n"
"	 trivial to extend to support new objects - simple objects are one\n"
"	 liners and complex objects only require the definition of a new\n"
"	 constructor.\n"
"      </para>\n"
"      <para>\n"
"         functionality have been plugged.  The <classname>Ssl</classname> class has received\n"
"         several new features relating to security.  Other areas have been\n"
"         improved: PRNG support, certificate and CRL signing, certificate chain\n"
"         and client verification.  Many bugs have been fixed, and certain\n"
"         parts of code re-written where necessary.  I hope you enjoy using POW \n"
"         and please feel free to send me feature requests and bug reports.\n"
"      </para>\n"
"   </body>\n"
"</moduleDescription>\n"
;

/*========== Pre-definitions ==========*/
static PyObject *SSLErrorObject;
static PyTypeObject x509type;
static PyTypeObject x509_storetype;
static PyTypeObject x509_crltype;
static PyTypeObject x509_revokedtype;
static PyTypeObject asymmetrictype;
static PyTypeObject symmetrictype;
static PyTypeObject digesttype;
static PyTypeObject hmactype;
static PyTypeObject ssltype;
/*========== Pre-definitions ==========*/

/*========== C stucts ==========*/
typedef struct {
	PyObject_HEAD
   X509 *x509;
} x509_object;

typedef struct {
	PyObject_HEAD
   X509_STORE *store;
} x509_store_object;

typedef struct {
	PyObject_HEAD
   X509_CRL *crl;
} x509_crl_object;

typedef struct {
	PyObject_HEAD
   X509_REVOKED *revoked;
} x509_revoked_object;

typedef struct {
	PyObject_HEAD
   void *cipher;
   int key_type;
   int cipher_type;
} asymmetric_object;

typedef struct {
	PyObject_HEAD
   EVP_CIPHER_CTX cipher_ctx;
   int cipher_type;
} symmetric_object;

typedef struct {
	PyObject_HEAD
   EVP_MD_CTX digest_ctx;
   int digest_type;
} digest_object;

typedef struct {
	PyObject_HEAD
   HMAC_CTX hmac_ctx;
} hmac_object;

typedef struct {
	PyObject_HEAD
   int ctxset;
   SSL *ssl;
   SSL_CTX *ctx;
} ssl_object;
/*========== C stucts ==========*/

/*========== helper funcitons ==========*/

/* 
   Simple function to install a constant in the module name space.
*/
static void
install_int_const( PyObject *d, char *name, int value )
{
   PyObject *v = PyInt_FromLong( (long)value );
   if (!v || PyDict_SetItemString(d, name, v) )
      PyErr_Clear();

   Py_XDECREF(v);
}

int
docset_helper_add(PyObject *set, char *v)
{
   PyObject *value=NULL;

   if ( !(value = PyString_FromString(v) ) )
      { PyErr_SetString( SSLErrorObject, "could not allocate memory" ); goto error; }

   if ( PyList_Append( set, value ) != 0)
      goto error;

   return 1;

error:

   Py_XDECREF(value);
   return 0;
}

/*
   Generate an encrypion envelope.  Saves a lot of space having thie case
   statement in one place.
*/
static EVP_CIPHER *
evp_cipher_factory(int cipher_type)
{
   switch(cipher_type)
   {
#ifndef NO_DES
      case DES_ECB:           return EVP_des_ecb();
      case DES_EDE:           return EVP_des_ede();
      case DES_EDE3:          return EVP_des_ede3();
      case DES_CFB:           return EVP_des_cfb();
      case DES_EDE_CFB:       return EVP_des_ede_cfb();
      case DES_EDE3_CFB:      return EVP_des_ede3_cfb();
      case DES_OFB:           return EVP_des_ofb();
      case DES_EDE_OFB:       return EVP_des_ede_ofb();
      case DES_EDE3_OFB:      return EVP_des_ede3_ofb();
      case DES_CBC:           return EVP_des_cbc();
      case DES_EDE_CBC:       return EVP_des_ede_cbc();
      case DES_EDE3_CBC:      return EVP_des_ede3_cbc();
      case DESX_CBC:          return EVP_desx_cbc();
#endif
#ifndef NO_RC4
      case RC4:               return EVP_rc4();
      case RC4_40:            return EVP_rc4_40();
#endif
#ifndef NO_IDEA
      case IDEA_ECB:          return EVP_idea_ecb();
      case IDEA_CFB:          return EVP_idea_cfb();
      case IDEA_OFB:          return EVP_idea_ofb();
      case IDEA_CBC:          return EVP_idea_cbc();
#endif
#ifndef NO_RC2
      case RC2_ECB:           return EVP_rc2_ecb();
      case RC2_CBC:           return EVP_rc2_cbc();
      case RC2_40_CBC:        return EVP_rc2_40_cbc();
      case RC2_CFB:           return EVP_rc2_cfb();
      case RC2_OFB:           return EVP_rc2_ofb();
#endif
#ifndef NO_BF
      case BF_ECB:            return EVP_bf_ecb();
      case BF_CBC:            return EVP_bf_cbc();
      case BF_CFB:            return EVP_bf_cfb();
      case BF_OFB:            return EVP_bf_ofb();
#endif
#ifndef NO_CAST5
      case CAST5_ECB:         return EVP_cast5_ecb();
      case CAST5_CBC:         return EVP_cast5_cbc();
      case CAST5_CFB:         return EVP_cast5_cfb();
      case CAST5_OFB:         return EVP_cast5_ofb();
#endif
#ifndef NO_RC5_32_12_16
      case RC5_32_12_16_CBC:  return EVP_rc5_32_12_16_cbc();
      case RC5_32_12_16_CFB:  return EVP_rc5_32_12_16_cfb();
      case RC5_32_12_16_ECB:  return EVP_rc5_32_12_16_ecb();
      case RC5_32_12_16_OFB:  return EVP_rc5_32_12_16_ofb();
#endif
      default:                return NULL;
   }
}

static PyObject *
ssl_err_factory(int err)
{
   switch(err)
   {
      case SSL_ERROR_NONE: 
         return Py_BuildValue( "(is)", SSL_ERROR_NONE, "SSL_ERROR_NONE" );
      case SSL_ERROR_ZERO_RETURN: 
         return Py_BuildValue( "(is)", SSL_ERROR_ZERO_RETURN, "SSL_ERROR_ZERO_RETURN" ); 
      case SSL_ERROR_WANT_READ:  
         return Py_BuildValue( "(is)", SSL_ERROR_WANT_READ, "SSL_ERROR_WANT_READ" );
      case SSL_ERROR_WANT_WRITE: 
         return Py_BuildValue( "(is)", SSL_ERROR_WANT_WRITE, "SSL_ERROR_WANT_WRITE" ); 
      case SSL_ERROR_WANT_X509_LOOKUP: 
         return Py_BuildValue( "(is)", SSL_ERROR_WANT_X509_LOOKUP, "SSL_ERROR_WANT_X509_LOOKUP" ); 
      case SSL_ERROR_SYSCALL: 
         return Py_BuildValue( "(is)", SSL_ERROR_SYSCALL, "SSL_ERROR_SYSCALL" ); 
      case SSL_ERROR_SSL: 
         return Py_BuildValue( "(is)", SSL_ERROR_SSL, "SSL_ERROR_SSL" ); 

      default:
         return Py_BuildValue( "(is)", err, "UNKOWN_SSL_ERROR" ); 
   }
}

static PyObject *
X509_object_helper_set_name(X509_NAME *name, PyObject *name_sequence)
{
   PyObject *pair = NULL; PyObject *type = NULL; PyObject *value = NULL;
   int no_pairs = 0, i = 0, str_type = 0, nid;
   char *valueptr = NULL, *typeptr = NULL;

   no_pairs = PySequence_Size( name_sequence );
   for (i=0; i < no_pairs; i++)
   {
      if ( ( pair = PySequence_GetItem( name_sequence, i ) ) == NULL  )
         return NULL;

      if ( !( PyTuple_Check(pair) || PyList_Check(pair) ) )
         { PyErr_SetString( PyExc_TypeError, "inapropriate type" ); goto error; }

      if ( PySequence_Size(pair) != 2 )
         { PyErr_SetString( SSLErrorObject, "each name entry must have 2 elements" ); goto error; }

      if ( !(type = PySequence_GetItem( pair, 0 ) ) )
         { PyErr_SetString( PyExc_TypeError, "could not get type string" ); goto error; }

      if ( !PyString_Check(type) )
         { PyErr_SetString( PyExc_TypeError, "inapropriate type" ); goto error; }

      if ( !( value = PySequence_GetItem( pair, 1 ) ) )
         { PyErr_SetString( PyExc_TypeError, "could not get value string" ); goto error; }

      if ( !PyString_Check(value) )
         { PyErr_SetString( PyExc_TypeError, "inapropriate type" ); goto error; }

      typeptr = PyString_AsString(type);
      valueptr = PyString_AsString(value);

      str_type = ASN1_PRINTABLE_type( valueptr, -1 );
      if ( !(nid = OBJ_ln2nid(typeptr)) )
         if ( !(nid = OBJ_sn2nid(typeptr)) )
            { PyErr_SetString( SSLErrorObject, "unknown ASN1 object" ); goto error; }

      if ( !X509_NAME_add_entry_by_NID( name, nid, str_type, valueptr, strlen(valueptr), -1, 0 ) )
         { PyErr_SetString( SSLErrorObject, "unable to add name entry" ); goto error; }

      Py_DECREF(pair);
      Py_DECREF(type);
      Py_DECREF(value);
      pair = NULL;
      type = NULL;
      value = NULL;
   }
   return name_sequence;

error:

   Py_XDECREF(pair);
   Py_XDECREF(type);
   Py_XDECREF(value);

   return NULL;
}

static PyObject *
X509_object_helper_get_name(X509_NAME *name, int format)
{
   int no_entries=0, no_pairs=0, i=0, j=0, value_len=0, nid=0;
   X509_NAME_ENTRY *entry=NULL;
   char *value=NULL, long_name[512];
   const char *short_name;

   PyObject *result_list = NULL;
   PyObject *pair = NULL;
   PyObject *py_type = NULL;
   PyObject *py_value = NULL;

   no_entries = X509_NAME_entry_count( name );

   if ( !(result_list = PyTuple_New( no_entries ) ) )
      { PyErr_SetString( SSLErrorObject, "could not allocate memory" ); goto error; }

   for(i=0; i<no_entries; i++)
   {
      if ( !(entry = X509_NAME_get_entry( name, i ) ) )
         { PyErr_SetString( SSLErrorObject, "could not get certificate name" ); goto error; }

      if (entry->value->length + 1 > value_len)
      {
         if (value)
            free(value);

         if ( !(value = malloc( entry->value->length + 1 ) ) )
            { PyErr_SetString( SSLErrorObject, "could not allocate memory" ); goto error; }

         value_len = entry->value->length + 1; 
      }
      memcpy( value, entry->value->data, entry->value->length );
      value[ entry->value->length ] = 0;

      if ( !(i2t_ASN1_OBJECT(long_name, sizeof(long_name), entry->object) ) )
         { PyErr_SetString( SSLErrorObject, "could not object name" ); goto error; }

      if ( format == SHORTNAME_FORMAT )
      {
         nid = OBJ_ln2nid( long_name );
         short_name = OBJ_nid2sn( nid );
         py_type = PyString_FromString(short_name);
      }
      else if ( format == LONGNAME_FORMAT )
         py_type = PyString_FromString(long_name);
      else
         { PyErr_SetString( SSLErrorObject, "unkown name format" ); goto error; }

      py_value = PyString_FromString(value);

      if ( !(pair = PyTuple_New( 2 ) ) )
         { PyErr_SetString( SSLErrorObject, "could not allocate memory" ); goto error; }

      PyTuple_SetItem( pair, 0, py_type );
      PyTuple_SetItem( pair, 1, py_value );
      PyTuple_SetItem( result_list, i, pair );
   }

   if (value)
      free(value);

   return result_list;

error:

   if (value)
      free(value);

   if (result_list)
   {
      no_pairs = PyTuple_Size( result_list );
      for (i=0; i < no_pairs; i++)
      {
         pair = PyTuple_GetItem( result_list, i );
         no_entries = PyTuple_Size( result_list );
         for (j=0; j < no_entries; j++)
         {
            py_value = PyTuple_GetItem( pair, i );
            Py_DECREF( py_value );
         }
      }
   }

   Py_XDECREF(py_type);
   Py_XDECREF(py_value);
   Py_XDECREF(result_list);
   return NULL;
}
/*========== helper funcitons ==========*/

/*========== X509 code ==========*/
static x509_object *
X509_object_new(void)
{
   x509_object *self;

   self = PyObject_New( x509_object, &x509type );
   if (self == NULL)
      goto error;

   self->x509 = X509_new();
   return self;

error:

   Py_XDECREF(self);
   return NULL;
}

/*
   This function is pretty dumb.  Most of the work is done by the module
   function pow_module_pem_read().
*/
static x509_object *
X509_object_pem_read(BIO *in)
{
   x509_object *self;

   if ( !(self = PyObject_New( x509_object, &x509type ) ) )
      goto error;

   if( !(self->x509 = PEM_read_bio_X509( in, NULL, NULL, NULL ) ) )
      { PyErr_SetString( SSLErrorObject, "could not load PEM encoded certificate" ); goto error; }

   return self;

error:

   Py_XDECREF(self);
   return NULL;
}

static x509_object *
X509_object_der_read(char *src, int len)
{
   x509_object *self;
   unsigned char *ptr = src;

   if ( !(self = PyObject_New( x509_object, &x509type ) ) )
      goto error;

   self->x509 = X509_new();

   if( !(d2i_X509( &self->x509, &ptr, len ) ) )
      { PyErr_SetString( SSLErrorObject, "could not load PEM encoded certificate" ); goto error; }

   return self;

error:

   Py_XDECREF(self);
   return NULL;
}

/*
   Unlike the previous function this creates the BIO itself.  The BIO_s_mem
   is used as a buffer which the certificate is read into, from this buffer
   it is read into a char[] and returned as a string.
*/
static PyObject *
X509_object_write_helper(x509_object *self, PyObject *args, int format)
{
   int len=0;
   char *buf=NULL;
   BIO *out_bio=NULL;
   PyObject *cert=NULL;
   
	if (!PyArg_ParseTuple(args, ""))
		return NULL;

   out_bio = BIO_new(BIO_s_mem());

   if (format == DER_FORMAT)
   {
      if (!i2d_X509_bio(out_bio, self->x509) )
         { PyErr_SetString( SSLErrorObject, "unable to write certificate" ); goto error; }
   }
   else if (format == PEM_FORMAT)
   {
      if (!PEM_write_bio_X509(out_bio, self->x509) )
         { PyErr_SetString( SSLErrorObject, "unable to write certificate" ); goto error; }
   }
   else
      { PyErr_SetString( SSLErrorObject, "internal error, unkown output format" ); goto error; }

   if ( !(len = BIO_ctrl_pending(out_bio) ) )
      { PyErr_SetString( SSLErrorObject, "unable to get bytes stored in bio" ); goto error; }

   if ( !(buf = malloc(len) ) )
      { PyErr_SetString( SSLErrorObject, "unable to allocate memory" ); goto error; }

   if ( BIO_read( out_bio, buf, len ) != len )
      { PyErr_SetString( SSLErrorObject, "unable to write out cert" ); goto error; }

   cert = Py_BuildValue("s#", buf, len);

   BIO_free(out_bio);
   free(buf);
   return cert;
   
error:   

   if (out_bio)
      BIO_free(out_bio);

   if (buf)
      free(buf);

   Py_XDECREF(cert);
   return NULL;
}

static char X509_object_pem_write__doc__[] = 
"<method>\n"
"   <header>\n"
"      <memberof>X509</memberof>\n"
"      <name>pemWrite</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method returns a PEM encoded certificate as a\n"
"         string.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
X509_object_pem_write(x509_object *self, PyObject *args)
{
   return X509_object_write_helper(self, args, PEM_FORMAT);
}

static char X509_object_der_write__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>X509</memberof>\n"
"      <name>derWrite</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method returns a DER encoded certificate as a\n"
"         string.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
X509_object_der_write(x509_object *self, PyObject *args)
{
   return X509_object_write_helper(self, args, DER_FORMAT);
}

/*
   Currently this function only supports RSA keys.
*/
static char X509_object_set_public_key__doc__[] = 
"<method>\n"
"   <header>\n"
"      <memberof>X509</memberof>\n"
"      <name>setPublicKey</name>\n"
"      <parameter>key</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method sets the public key for this certificate object.  The\n"
"         parameter <parameter>key</parameter> should be an instance of\n"
"         <classname>Asymmetric</classname> containing a public key.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;


static PyObject *
X509_object_set_public_key(x509_object *self, PyObject *args)
{
	EVP_PKEY *pkey=NULL;
   asymmetric_object *asym;

	if (!PyArg_ParseTuple(args, "O!", &asymmetrictype, &asym))
		goto error;

   if ( !(pkey = EVP_PKEY_new() ) )
      { PyErr_SetString( SSLErrorObject, "could not allocate memory" ); goto error; }

   if ( !(EVP_PKEY_assign_RSA(pkey, asym->cipher) ) )
      { PyErr_SetString( SSLErrorObject, "EVP_PKEY assignment error" ); goto error; }

	if ( !(X509_set_pubkey(self->x509,pkey) ) )
      { PyErr_SetString( SSLErrorObject, "could not set certificate's public key" ); goto error; }

   return Py_BuildValue("");

error:

   if (pkey)
      EVP_PKEY_free(pkey);

   return NULL;

}

static char X509_object_sign__doc__[] = 
"<method>\n"
"   <header>\n"
"      <memberof>X509</memberof>\n"
"      <name>sign</name>\n"
"      <parameter>key</parameter>\n"
"      <parameter>digest=MD5_DIGEST</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method signs a certificate with a private key.  See the\n"
"         example for the methods which should be invoked before signing a\n"
"         certificate.  <parameter>key</parameter> should be an instance of\n"
"         <classname>Asymmetric</classname> containing a private key.\n"
"         The optional parameter <parameter>digest</parameter> indicates \n"
"         which digest function should be used to compute the hash to be \n"
"         signed, it should be one of the following:\n"
"      </para>\n"
"      <simplelist>\n"
"         <member><constant>MD2_DIGEST</constant></member>\n"
"         <member><constant>MD5_DIGEST</constant></member>\n"
"         <member><constant>SHA_DIGEST</constant></member>\n"
"         <member><constant>SHA1_DIGEST</constant></member>\n"
"         <member><constant>RIPEMD160_DIGEST</constant></member>\n"
"     </simplelist>\n"
"   </body>\n"
"</method>\n"
;


static PyObject *
X509_object_sign(x509_object *self, PyObject *args)
{
	EVP_PKEY *pkey=NULL;
   asymmetric_object *asym;
   int digest=MD5_DIGEST;

	if (!PyArg_ParseTuple(args, "O!|i", &asymmetrictype, &asym, &digest))
		goto error;

   if ( !(pkey = EVP_PKEY_new() ) )
      { PyErr_SetString( SSLErrorObject, "could not allocate memory" ); goto error; }

   if (asym->key_type != RSA_PRIVATE_KEY)
      { PyErr_SetString( SSLErrorObject, "cannot use this type of key" ); goto error; }

   if ( !(EVP_PKEY_assign_RSA(pkey, asym->cipher) ) )
      { PyErr_SetString( SSLErrorObject, "EVP_PKEY assignment error" ); goto error; }

   switch (digest)
   {
      case MD5_DIGEST:
      { 
         if (!X509_sign(self->x509, pkey, EVP_md5() ) ) 
            { PyErr_SetString( SSLErrorObject, "could not sign certificate" ); goto error; }
         break;
      }
      case MD2_DIGEST:
      { 
         if (!X509_sign(self->x509, pkey, EVP_md2() ) ) 
            { PyErr_SetString( SSLErrorObject, "could not sign certificate" ); goto error; }
         break;
      }
      case SHA_DIGEST:
      { 
         if (!X509_sign(self->x509, pkey, EVP_sha() ) ) 
            { PyErr_SetString( SSLErrorObject, "could not sign certificate" ); goto error; }
         break;
      }
      case SHA1_DIGEST:
      { 
         if (!X509_sign(self->x509, pkey, EVP_sha1() ) ) 
            { PyErr_SetString( SSLErrorObject, "could not sign certificate" ); goto error; }
         break;
      }
      case RIPEMD160_DIGEST:
      { 
         if (!X509_sign(self->x509, pkey, EVP_ripemd160() ) ) 
            { PyErr_SetString( SSLErrorObject, "could not sign certificate" ); goto error; }
         break;
      }
   }

   return Py_BuildValue("");

error:

   if (pkey)
      EVP_PKEY_free(pkey);

   return NULL;

}

static char X509_object_get_version__doc__[] = 
"<method>\n"
"   <header>\n"
"      <memberof>X509</memberof>\n"
"      <name>getVersion</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method returns the version number from the version field of\n"
"         this certificate. \n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;


static PyObject *
X509_object_get_version(x509_object *self, PyObject *args)
{
   long version=0;

	if (!PyArg_ParseTuple(args, ""))
		goto error;

   if ( !(version = X509_get_version( self->x509 ) ) )
      { PyErr_SetString( SSLErrorObject, "could not get certificate version" ); goto error; }

   return Py_BuildValue("l", version);

error:

   return NULL;
}

static char X509_object_set_version__doc__[] = 
"<method>\n"
"   <header>\n"
"      <memberof>X509</memberof>\n"
"      <name>setVersion</name>\n"
"      <parameter>version</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method sets the version number in the version field of\n"
"         this certificate.  <parameter>version</parameter> should be an\n"
"         integer.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
X509_object_set_version(x509_object *self, PyObject *args)
{
   long version=0;

	if (!PyArg_ParseTuple(args, "l", &version))
		goto error;

   if ( !X509_set_version( self->x509, version ) )
      { PyErr_SetString( SSLErrorObject, "could not set certificate version" ); goto error; }

   return Py_BuildValue("");

error:

   return NULL;
}

static char X509_object_get_serial__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>X509</memberof>\n"
"      <name>getSerial</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method get the serial number in the serial field of\n"
"         this certificate.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
X509_object_get_serial(x509_object *self, PyObject *args)
{
   long serial=0;
   ASN1_INTEGER *asn1i=NULL;

	if (!PyArg_ParseTuple(args, ""))
		goto error;

   if ( !(asn1i = X509_get_serialNumber( self->x509 ) ) )
      { PyErr_SetString( SSLErrorObject, "could not get serial number" ); goto error; }

   if ( (serial = ASN1_INTEGER_get(asn1i) ) == -1 )
      { PyErr_SetString( SSLErrorObject, "could not convert ASN1 Integer to long" ); goto error; }

   return Py_BuildValue("l", serial);

error:

   return NULL;
}

static char X509_object_set_serial__doc__[] = 
"<method>\n"
"   <header>\n"
"      <memberof>X509</memberof>\n"
"      <name>setSerial</name>\n"
"      <parameter>serial</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method sets the serial number in the serial field of\n"
"         this certificate.  <parameter>serial</parameter> should ba an\n"
"         integer.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
X509_object_set_serial(x509_object *self, PyObject *args)
{
   long serial=0;
   ASN1_INTEGER *asn1i=NULL;

	if (!PyArg_ParseTuple(args, "l", &serial))
		goto error;

   if ( !(asn1i = ASN1_INTEGER_new() ) )
      { PyErr_SetString( SSLErrorObject, "could not allocate memory" ); goto error; }

   if ( !ASN1_INTEGER_set( asn1i, serial ) )
      { PyErr_SetString( SSLErrorObject, "could not set ASN1 integer" ); goto error; }

   if ( !X509_set_serialNumber( self->x509, asn1i ) )
      { PyErr_SetString( SSLErrorObject, "could not set certificate serial" ); goto error; }

   ASN1_INTEGER_free(asn1i);

   return Py_BuildValue("");

error:

   if (asn1i)
      ASN1_INTEGER_free(asn1i);

   return NULL;
}

static char X509_object_get_issuer__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>X509</memberof>\n"
"      <name>getIssuer</name>\n"
"      <parameter>format=SHORTNAME_FORMAT</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method returns a tuple containing the issuers name.  Each\n"
"         element of the tuple is a tuple with 2 elements.  The first tuple\n"
"         is an object name and the second is it's value.  Both issuer and\n"
"         subject are names distinguished normally composed of a small\n"
"         number of objects:\n"
"      </para>\n"
"      <simplelist>\n"
"         <member><constant>c</constant> or <constant>countryName</constant></member>\n"
"         <member><constant>st</constant> or <constant>stateOrProvinceName</constant></member>\n"
"         <member><constant>o</constant> or <constant>organizationName</constant></member>\n"
"         <member><constant>l</constant> or <constant>localityName</constant></member>\n"
"         <member><constant>ou</constant> or <constant>organizationalUnitName</constant></member>\n"
"         <member><constant>cn</constant> or <constant>commonName</constant></member>\n"
"      </simplelist>\n"
"      <para>\n"
"         The data type varies from one object to another, however, all the\n"
"         common objects are strings.  It would be possible to specify any\n"
"         kind of object but that would certainly adversely effect\n"
"         portability and is not recommended.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
X509_object_get_issuer(x509_object *self, PyObject *args)
{
   PyObject *result_list = NULL;
   X509_NAME *name = NULL;
   int format=SHORTNAME_FORMAT;

	if (!PyArg_ParseTuple(args, "|i", &format))
		goto error;

   if ( !(name = X509_get_issuer_name( self->x509 ) ) )
      { PyErr_SetString( SSLErrorObject, "could not get issuers name" ); goto error; }

   if ( !(result_list = X509_object_helper_get_name(name, format) ) )
      { PyErr_SetString( SSLErrorObject, "failed to produce name list" ); goto error; }

   return result_list;

error:

   return NULL;
}

static char X509_object_get_subject__doc__[] = 
"<method>\n"
"   <header>\n"
"      <memberof>X509</memberof>\n"
"      <name>getSubject</name>\n"
"      <parameter>format=SHORTNAME_FORMAT</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method returns a tuple containing the subjects name.  See\n"
"         <function>getIssuer</function> for a description of the returned\n"
"         object's format.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
X509_object_get_subject(x509_object *self, PyObject *args)
{
   PyObject *result_list = NULL;
   X509_NAME *name = NULL;
   int format=SHORTNAME_FORMAT;

	if (!PyArg_ParseTuple(args, "|i", &format))
		goto error;

   if ( !(name = X509_get_subject_name( self->x509 ) ) )
      { PyErr_SetString( SSLErrorObject, "could not get issuers name" ); goto error; }

   if ( !(result_list = X509_object_helper_get_name(name, format) ) )
      { PyErr_SetString( SSLErrorObject, "failed to produce name list" ); goto error; }

   return result_list;

error:

   return NULL;
}

static char X509_object_set_subject__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>X509</memberof>\n"
"      <name>setSubject</name>\n"
"      <parameter>name</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method is used to set the subjects name.\n"
"         <parameter>name</parameter> can be comprised of lists or tuples in\n"
"         the format described in the <function>getIssuer</function> method.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
X509_object_set_subject(x509_object *self, PyObject *args)
{
   PyObject *name_sequence = NULL;
   X509_NAME *name = NULL;

	if (!PyArg_ParseTuple(args, "O", &name_sequence))
		goto error;

   if ( !( PyTuple_Check( name_sequence ) || PyList_Check(name_sequence) ) )
      { PyErr_SetString( PyExc_TypeError, "Inapropriate type" ); goto error; }

   if ( !(name = X509_NAME_new() ) )
      { PyErr_SetString( SSLErrorObject, "could not allocate memory" ); goto error; }

   if ( !X509_object_helper_set_name(name, name_sequence) )
      { PyErr_SetString( SSLErrorObject, "unable to set new name" ); goto error; }

	if ( !X509_set_subject_name(self->x509,name) )
      { PyErr_SetString( SSLErrorObject, "unable to set name" ); goto error; }
   
   X509_NAME_free(name);

   return Py_BuildValue("");

error:

   return NULL;
}

static char X509_object_set_issuer__doc__[] = 
"<method>\n"
"   <header>\n"
"      <memberof>X509</memberof>\n"
"      <name>setIssuer</name>\n"
"      <parameter>name</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method is used to set the issuers name.\n"
"         <parameter>name</parameter> can be comprised of lists or tuples in\n"
"         the format described in the <function>getissuer</function> method.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
X509_object_set_issuer(x509_object *self, PyObject *args)
{
   PyObject *name_sequence = NULL;
   X509_NAME *name = NULL;

	if (!PyArg_ParseTuple(args, "O", &name_sequence))
		goto error;

   if ( !( PyTuple_Check( name_sequence ) || PyList_Check(name_sequence) ) )
      { PyErr_SetString( PyExc_TypeError, "Inapropriate type" ); goto error; }

   if ( !(name = X509_NAME_new() ) )
      { PyErr_SetString( SSLErrorObject, "could not allocate memory" ); goto error; }

   if ( !X509_object_helper_set_name(name, name_sequence) )
      { PyErr_SetString( SSLErrorObject, "unable to set new name" ); goto error; }

	if ( !X509_set_issuer_name(self->x509,name) )
      { PyErr_SetString( SSLErrorObject, "unable to set name" ); goto error; }

   X509_NAME_free(name);

   return Py_BuildValue("");

error:

   if (name)
      X509_NAME_free(name);

   return  NULL;
}

static char X509_object_get_not_before__doc__[] = 
"<method>\n"
"   <header>\n"
"      <memberof>X509</memberof>\n"
"      <name>getNotBefore</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         In a change from previous releases, for reasons of portability\n"
"         and to avoid hard to fix issues with problems in unreliable time\n"
"         functions, this function returns a UTCTime string.  You\n"
"         can use the function <function>time2utc</function> to convert to a\n"
"         string if you like and <function>utc2time</function> to back.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"

;

static PyObject *
X509_object_get_not_before (x509_object *self, PyObject *args)
{
   ASN1_UTCTIME *time;

	if (!PyArg_ParseTuple(args, ""))
		goto error;

   return Py_BuildValue("s", self->x509->cert_info->validity->notBefore->data);

error:

   return NULL;
}

static char X509_object_get_not_after__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>X509</memberof>\n"
"      <name>getNotAfter</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         In a change from previous releases, for reasons of portability\n"
"         and to avoid hard to fix issues with problems in unreliable time\n"
"         functions, this function returns a UTCTime string.  You\n"
"         can use the function <function>time2utc</function> to convert to a\n"
"         string if you like and <function>utc2time</function> to back.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
X509_object_get_not_after (x509_object *self, PyObject *args)
{
   ASN1_UTCTIME *time=NULL;

	if (!PyArg_ParseTuple(args, ""))
		goto error;

   return Py_BuildValue("s", self->x509->cert_info->validity->notAfter->data);

error:

   return NULL;
}

static char X509_object_set_not_after__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>X509</memberof>\n"
"      <name>setNotAfter</name>\n"
"      <parameter>time</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         In a change from previous releases, for reasons of portability\n"
"         and to avoid hard to fix issues with problems in unreliable time\n"
"         functions, this accepts one parameter, a UTCTime string.  You\n"
"         can use the function <function>time2utc</function> to convert to a\n"
"         string if you like and <function>utc2time</function> to back.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
X509_object_set_not_after (x509_object *self, PyObject *args)
{
   //int new_time = 0;
   char *new_time=NULL;

	if (!PyArg_ParseTuple(args, "s", &new_time))
		goto error;

	if ( !ASN1_UTCTIME_set_string(self->x509->cert_info->validity->notAfter, new_time) )
      { PyErr_SetString( SSLErrorObject, "could not set time" ); goto error; }

   return Py_BuildValue("");

error:

   return NULL;
}

static char X509_object_set_not_before__doc__[] = 
"<method>\n"
"   <header>\n"
"      <memberof>X509</memberof>\n"
"      <name>setNotBefore</name>\n"
"      <parameter>time</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         In a change from previous releases, for reasons of portability\n"
"         and to avoid hard to fix issues with problems in unreliable time\n"
"         functions, this accepts one parameter, a UTCTime string.  You\n"
"         can use the function <function>time2utc</function> to convert to a\n"
"         string if you like and <function>utc2time</function> to back.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
X509_object_set_not_before (x509_object *self, PyObject *args)
{
   //int new_time = 0;
   char *new_time=NULL;

	if (!PyArg_ParseTuple(args, "s", &new_time))
		goto error;

	if ( !ASN1_UTCTIME_set_string(self->x509->cert_info->validity->notBefore, new_time) )
      { PyErr_SetString( SSLErrorObject, "could not set time" ); goto error; }

   return Py_BuildValue("");

error:

   return NULL;
}

static char X509_object_add_extension__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>X509</memberof>\n"
"      <name>addExtension</name>\n"
"      <parameter>extensionName</parameter>\n"
"      <parameter>critical</parameter>\n"
"      <parameter>extensionValue</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method adds an extension to this certificate.\n"
"         <parameter>extensionName</parameter> should be the of the\n"
"         extension.  <parameter>critical</parameter> should an integer, 1\n"
"         for true and 0 for false.  <parameter>extensionValue</parameter>\n"
"         should be a string, DER encoded value of the extension.  The name\n"
"         of the extension must be correct according to OpenSSL and can be\n"
"         checked in the <constant>objects.h</constant> header file, part of\n"
"         the OpenSSL source distribution.  In the majority of cases they\n"
"         are the same as those defined in <constant>POW._oids</constant>\n"
"         but if you do encounter problems is may be worth checking.\n"
"      </para>\n"
"      <example>\n"
"         <title><function>addExtension</function> method usage</title>\n"
"         <programlisting>\n"
"      basic = POW.pkix.BasicConstraints()\n"
"      basic.set([1,5]) \n"
"      serverCert.addExtension( 'basicConstraints', 0, basic.toString())\n"
"         </programlisting>\n"
"      </example>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
X509_object_add_extension(x509_object *self, PyObject *args)
{
   int critical=0, nid=0;
   char *name=NULL, *buf=NULL;
   ASN1_OCTET_STRING *octetString=NULL;
   X509_EXTENSION *extn=NULL;

	if (!PyArg_ParseTuple(args, "sis", &name, &critical, &buf))
		goto error;

   if ( !(octetString = M_ASN1_OCTET_STRING_new() ) )
      { PyErr_SetString( SSLErrorObject, "could not allocate memory" ); goto error; }

   if ( !ASN1_OCTET_STRING_set(octetString, buf, strlen(buf)) )
      { PyErr_SetString( SSLErrorObject, "could not set ASN1 Octect string" ); goto error; }

   if ( NID_undef == (nid = OBJ_txt2nid(name) ) )
      { PyErr_SetString( SSLErrorObject, "extension has unknown object identifier" ); goto error; }

   if ( !( extn = X509_EXTENSION_create_by_NID(NULL, nid, critical, octetString) ) )
      { PyErr_SetString( SSLErrorObject, "unable to create ASN1 X509 Extension object" ); goto error; }

   if (!self->x509->cert_info->extensions)
      if ( !(self->x509->cert_info->extensions = sk_X509_EXTENSION_new_null() ) ) 
         { PyErr_SetString( SSLErrorObject, "unable to allocate memory" ); goto error; }

   if ( !sk_X509_EXTENSION_push(self->x509->cert_info->extensions, extn) )
      { PyErr_SetString( SSLErrorObject, "unable to add extension" ); goto error; }

   return Py_BuildValue("");

error:

   if(extn)
      X509_EXTENSION_free(extn);
 
   return NULL;
}

static char X509_object_clear_extensions__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>X509</memberof>\n"
"      <name>clearExtensions</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method clears the structure which holds the extension for\n"
"         this certificate.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
X509_object_clear_extensions(x509_object *self, PyObject *args)
{
	if (!PyArg_ParseTuple(args, ""))
		goto error;

   if (self->x509->cert_info->extensions)
   {
      sk_X509_EXTENSION_free(self->x509->cert_info->extensions);
      self->x509->cert_info->extensions=NULL;
   }

   return Py_BuildValue("");

error:

   return NULL;
}

static char X509_object_count_extensions__doc__[] = 
"<method>\n"
"   <header>\n"
"      <memberof>X509</memberof>\n"
"      <name>countExtensions</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method returns the size of the structure which holds the\n"
"         extension for this certificate.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
X509_object_count_extensions(x509_object *self, PyObject *args)
{
   int num=0;
	if (!PyArg_ParseTuple(args, ""))
		goto error;

   if (self->x509->cert_info->extensions)
   {
      num = sk_X509_EXTENSION_num(self->x509->cert_info->extensions);
      return Py_BuildValue("i", num);
   }
   else
      return Py_BuildValue("i", 0);

error:

   return NULL;
}

static char X509_object_get_extension__doc__[] = 
"<method>\n"
"   <header>\n"
"      <memberof>X509</memberof>\n"
"      <name>getExtension</name>\n"
"      <parameter>index</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method returns a tuple equivalent the parameters of\n"
"         <function>addExtension</function>.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
X509_object_get_extension(x509_object *self, PyObject *args)
{
   int num=0, index=0, ext_nid=0;
   char const *ext_ln=NULL;
   char unknown_ext [] = "unkown";
   X509_EXTENSION *ext;
	if (!PyArg_ParseTuple(args, "i", &index))
		goto error;

   if (self->x509->cert_info->extensions)
   {
      num = sk_X509_EXTENSION_num(self->x509->cert_info->extensions);
   }
   else
      num = 0;

   if (index >= num)
      { PyErr_SetString( SSLErrorObject, "certificate does not have that many extensions" ); goto error; }

   if ( !(ext = sk_X509_EXTENSION_value(self->x509->cert_info->extensions, index) ) )
      { PyErr_SetString( SSLErrorObject, "could not get extension" ); goto error; }

   if ( NID_undef == (ext_nid = OBJ_obj2nid(ext->object) ) )
      { PyErr_SetString( SSLErrorObject, "extension has unknown object identifier" ); goto error; }

   if ( NULL == (ext_ln = OBJ_nid2sn(ext_nid) ) )
      ext_ln = unknown_ext;

   return Py_BuildValue("sis", ext_ln, ext->critical, ext->value->data );

error:

   return NULL;
}

static char x509_object_pprint__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>X509</memberof>\n"
"      <name>pprint</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method returns a formatted string showing the information\n"
"         held in the certificate.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
x509_object_pprint(x509_object *self, PyObject *args)
{
   int len=0, ret=0;
   char *buf=NULL;
   BIO *out_bio=NULL;
   PyObject *cert=NULL;
   
	if (!PyArg_ParseTuple(args, ""))
		goto error;

   out_bio = BIO_new(BIO_s_mem());

   if (!X509_print(out_bio, self->x509) )
      { PyErr_SetString( SSLErrorObject, "unable to write crl" ); goto error; }

   if ( !(len = BIO_ctrl_pending(out_bio) ) )
      { PyErr_SetString( SSLErrorObject, "unable to get bytes stored in bio" ); goto error; }

   if ( !(buf = malloc(len) ) )
      { PyErr_SetString( SSLErrorObject, "unable to allocate memory" ); goto error; }

   if ( (ret = BIO_read( out_bio, buf, len ) ) != len )
      { PyErr_SetString( SSLErrorObject, "unable to write out cert" ); goto error; }

   cert = Py_BuildValue("s#", buf, len);

   BIO_free(out_bio);
   free(buf);
   return cert;
   
error:   

   if (out_bio)
      BIO_free(out_bio);

   if (buf)
      free(buf);

   return NULL;

}

static struct PyMethodDef X509_object_methods[] = {
   {"pemWrite",      (PyCFunction)X509_object_pem_write,       METH_VARARGS,  NULL}, 
   {"derWrite",      (PyCFunction)X509_object_der_write,       METH_VARARGS,  NULL}, 
   {"sign",          (PyCFunction)X509_object_sign,            METH_VARARGS,  NULL}, 
   {"setPublicKey",  (PyCFunction)X509_object_set_public_key,  METH_VARARGS,  NULL}, 
   {"getVersion",    (PyCFunction)X509_object_get_version,     METH_VARARGS,  NULL}, 
   {"setVersion",    (PyCFunction)X509_object_set_version,     METH_VARARGS,  NULL}, 
   {"getSerial",     (PyCFunction)X509_object_get_serial,      METH_VARARGS,  NULL}, 
   {"setSerial",     (PyCFunction)X509_object_set_serial,      METH_VARARGS,  NULL}, 
   {"getIssuer",     (PyCFunction)X509_object_get_issuer,      METH_VARARGS,  NULL}, 
   {"setIssuer",     (PyCFunction)X509_object_set_issuer,      METH_VARARGS,  NULL}, 
   {"getSubject",    (PyCFunction)X509_object_get_subject,     METH_VARARGS,  NULL}, 
   {"setSubject",    (PyCFunction)X509_object_set_subject,     METH_VARARGS,  NULL}, 
   {"getNotBefore",  (PyCFunction)X509_object_get_not_before,  METH_VARARGS,  NULL}, 
   {"getNotAfter",   (PyCFunction)X509_object_get_not_after,   METH_VARARGS,  NULL}, 
   {"setNotAfter",   (PyCFunction)X509_object_set_not_after,   METH_VARARGS,  NULL}, 
   {"setNotBefore",  (PyCFunction)X509_object_set_not_before,  METH_VARARGS,  NULL}, 
   {"addExtension",  (PyCFunction)X509_object_add_extension,   METH_VARARGS,  NULL}, 
   {"clearExtensions",(PyCFunction)X509_object_clear_extensions,  METH_VARARGS,  NULL}, 
   {"countExtensions",(PyCFunction)X509_object_count_extensions,  METH_VARARGS,  NULL}, 
   {"getExtension", (PyCFunction)X509_object_get_extension,    METH_VARARGS,  NULL}, 
   {"pprint",        (PyCFunction)x509_object_pprint,          METH_VARARGS,  NULL}, 
 
	{NULL,		NULL}		/* sentinel */
};

static PyObject *
X509_object_getattr(x509_object *self, char *name)
{
	return Py_FindMethod(X509_object_methods, (PyObject *)self, name);
}

static void
X509_object_dealloc(x509_object *self, char *name)
{
   X509_free( self->x509 );
   PyObject_Del(self);
}

static char x509type__doc__[] =
"<class>\n"
"   <header>\n"
"      <name>X509</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This class provides access to a significant proportion of X509 \n"
"         functionality of OpenSSL.\n"
"      </para>\n"
"\n"
"      <example>\n"
"         <title><classname>x509</classname> class usage</title>\n"
"         <programlisting>\n"
"      privateFile = open('test/private.key', 'r')\n"
"      publicFile = open('test/public.key', 'r')\n"
"      certFile = open('test/cacert.pem', 'w')\n"
"\n"
"      publicKey = POW.pemRead(POW.RSA_PUBLIC_KEY, publicFile.read())\n"
"      privateKey = POW.pemRead(POW.RSA_PRIVATE_KEY, privateFile.read(), 'pass')\n"
"\n"
"      c = POW.X509()\n"
"\n"
"      name = [  ['C', 'GB'], ['ST', 'Hertfordshire'], \n"
"                ['O','The House'], ['CN', 'Peter Shannon'] ]\n"
"\n"
"      c.setIssuer( name )\n"
"      c.setSubject( name )\n"
"      c.setSerial(0)\n"
"      t1 = POW.pkix.time2utc( time.time() )     \n"
"      t2 = POW.pkix.time2utc( time.time() + 60*60*24*365)     \n"
"      c.setNotBefore(t1)\n"
"      c.setNotAfter(t2)\n"
"      c.setPublicKey(publicKey)\n"
"      c.sign(privateKey)\n"
"\n"
"      certFile.write( c.pemWrite() )\n"
"\n"
"      privateFile.close()\n"
"      publicFile.close()\n"
"      certFile.close()\n"
"         </programlisting>\n"
"      </example>\n"
"\n"
"   </body>\n"
"</class>\n"
;

static PyTypeObject x509type = {
	PyObject_HEAD_INIT(0)
	0,				                        /*ob_size*/
	"X509",			                     /*tp_name*/
	sizeof(x509_object),		            /*tp_basicsize*/
	0,				                        /*tp_itemsize*/
	(destructor)X509_object_dealloc,	   /*tp_dealloc*/
	(printfunc)0,		                  /*tp_print*/
	(getattrfunc)X509_object_getattr,   /*tp_getattr*/
	(setattrfunc)0,	                  /*tp_setattr*/
	(cmpfunc)0,		                     /*tp_compare*/
	(reprfunc)0,      		            /*tp_repr*/
	0,			                           /*tp_as_number*/
	0,		                              /*tp_as_sequence*/
	0,		                              /*tp_as_mapping*/
	(hashfunc)0,		                  /*tp_hash*/
	(ternaryfunc)0,		               /*tp_call*/
	(reprfunc)0,		                  /*tp_str*/
	0,
   0,
   0,
   0,
	x509type__doc__                     /* Documentation string */
};
/*========== X509 Code ==========*/

/*========== x509 store Code ==========*/
static x509_store_object *
x509_store_object_new(void)
{
   x509_store_object *self=NULL;

   self = PyObject_New( x509_store_object, &x509_storetype );
   if (self == NULL)
      goto error;

   self->store = X509_STORE_new();

   return self;

error:

   Py_XDECREF(self);
   return NULL;
}

static char x509_store_object_verify__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>X509Store</memberof>\n"
"      <name>verify</name>\n"
"      <parameter>certificate</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         The <classname>X509Store</classname> method\n"
"         <function>verify</function> is based on the\n"
"         <function>X509_verify_cert</function>.  It handles certain aspects\n"
"         of verification but not others.  The certificate will be verified\n"
"         against <constant>notBefore</constant>, \n"
"         <constant>notAfter</constant> and trusted certificates.\n"
"         It crucially will not handle checking the certificate against\n"
"         CRLs.  This functionality will probably make it into OpenSSL\n"
"         0.9.7.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
x509_store_object_verify(x509_store_object *self, PyObject *args)
{
   X509_STORE_CTX csc;
   x509_object *x509=NULL;
   int result=0;

	if (!PyArg_ParseTuple(args, "O!", &x509type, &x509))
		goto error;

   X509_STORE_CTX_init( &csc, self->store, x509->x509, NULL );
   result = X509_verify_cert( &csc );

   X509_STORE_CTX_cleanup( &csc );

   return Py_BuildValue("i", result);

error:

   return NULL;
}

static char x509_store_object_verify_chain__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>X509Store</memberof>\n"
"      <name>verifyChain</name>\n"
"      <parameter>certificate</parameter>\n"
"      <parameter>chain</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         The <classname>X509Store</classname> method <function>verifyChain</function> \n"
"         is based on the <function>X509_verify_cert</function> but is initialised \n"
"         with a <classname>X509</classname> object to verify and list of \n"
"         <classname>X509</classname> objects which form a chain to a trusted \n"
"         certificate.  Certain aspects of the verification are handled but not others.  \n"
"         The certificates will be verified against <constant>notBefore</constant>, \n"
"         <constant>notAfter</constant> and trusted certificates.  It crucially will \n"
"         not handle checking the certificate against CRLs.  This functionality will \n"
"         probably make it into OpenSSL 0.9.7.\n"
"      </para>\n"
"      <para>\n"
"         This may all sound quite straight forward but determining the \n"
"         certificate associated with the signature on another certificate\n"
"         can be very time consuming.  The management aspects of\n"
"         certificates are addressed by various V3 extensions which are not\n"
"         currently supported.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
x509_store_object_verify_chain(x509_store_object *self, PyObject *args)
{
   PyObject *x509_sequence=NULL;
   X509_STORE_CTX csc;
   x509_object *x509=NULL, *tmpX509=NULL;
   STACK_OF(X509) *x509_stack=NULL;
   int result=0, size=0, i=0;

	if (!PyArg_ParseTuple(args, "O!O", &x509type, &x509, &x509_sequence))
		goto error;

   if ( !( PyTuple_Check( x509_sequence ) || PyList_Check(x509_sequence) ) )
      { PyErr_SetString( PyExc_TypeError, "inapropriate type" ); goto error; }

   size = PySequence_Size( x509_sequence );

   if (!(x509_stack = sk_X509_new_null() ) )
      { PyErr_SetString( SSLErrorObject, "could not create new x509 stack" ); goto error; }

   for (i=0; i < size; i++)
   {
      if ( !( tmpX509 = (x509_object*)PySequence_GetItem( x509_sequence, i ) ) )
         goto error;

      if ( !X_X509_Check( tmpX509 ) )
         { PyErr_SetString( PyExc_TypeError, "inapropriate type" ); goto error; }

      if (!sk_X509_push( x509_stack, tmpX509->x509 ) )
         { PyErr_SetString( SSLErrorObject, "could not add x509 to stack" ); goto error; }
      Py_DECREF(tmpX509);
      tmpX509 = NULL;
   }

   X509_STORE_CTX_init( &csc, self->store, x509->x509, x509_stack );
   result = X509_verify_cert( &csc );

   X509_STORE_CTX_cleanup( &csc );
   sk_X509_free(x509_stack);
   return Py_BuildValue("i", result);

error:

   if(x509_stack)
      sk_X509_free(x509_stack);

   Py_XDECREF(tmpX509);

   return NULL;
}

static char x509_store_object_add_trust__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>X509Store</memberof>\n"
"      <name>addTrust</name>\n"
"      <parameter>cert</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method adds a new certificate to the store to be used in the\n"
"         verification process.  <parameter>cert</parameter> should be an\n"
"         instance of <classname>X509</classname>.  Using trusted certificates to manage\n"
"         verification is relatively primitive, more sophisticated systems\n"
"         can be constructed at an application level by by constructing\n"
"         certificate chains to verify. \n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
x509_store_object_add_trust(x509_store_object *self, PyObject *args)
{
   x509_object *x509=NULL;

	if (!PyArg_ParseTuple(args, "O!", &x509type, &x509))
		goto error;

   X509_STORE_add_cert( self->store, x509->x509 );

   return Py_BuildValue("");

error:

   return NULL;
}

static char x509_store_object_add_crl__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>X509Store</memberof>\n"
"      <name>addCrl</name>\n"
"      <parameter>crl</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method adds a CRL to a store to be used for verification.\n"
"         <parameter>crl</parameter> should be an instance of\n"
"         <classname>X509Crl</classname>.\n"
"         Unfortunately, the current stable release of OpenSSL does not\n"
"         support CRL checking for certificate verification.\n"
"         This functionality will probably make it into OpenSSL 0.9.7, until\n"
"         it does this function is useless and CRL verification must be\n"
"         implemented by the application.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
x509_store_object_add_crl(x509_store_object *self, PyObject *args)
{
   x509_crl_object *crl=NULL;

	if (!PyArg_ParseTuple(args, "O!", &x509_crltype, &crl))
		goto error;

   X509_STORE_add_crl( self->store, crl->crl );

   return Py_BuildValue("");

error:

   return NULL;
}

static struct PyMethodDef x509_store_object_methods[] = {
   {"verify",           (PyCFunction)x509_store_object_verify,       METH_VARARGS,  NULL}, 
   {"verifyChain",      (PyCFunction)x509_store_object_verify_chain, METH_VARARGS,  NULL}, 
   {"addTrust",         (PyCFunction)x509_store_object_add_trust,    METH_VARARGS,  NULL}, 
   {"addCrl",           (PyCFunction)x509_store_object_add_crl,      METH_VARARGS,  NULL}, 
 
	{NULL,		NULL}		/* sentinel */
};

static PyObject *
x509_store_object_getattr(x509_store_object *self, char *name)
{
	return Py_FindMethod(x509_store_object_methods, (PyObject *)self, name);
}

static void
x509_store_object_dealloc(x509_store_object *self, char *name)
{
   X509_STORE_free( self->store );
   PyObject_Del(self);
}

static char x509_storetype__doc__[] =
"<class>\n"
"   <header>\n"
"      <name>X509Store</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This class provides preliminary access to OpenSSL X509 verification\n"
"         facilities.\n"
"      </para>\n"
"\n"
"      <example>\n"
"         <title><classname>x509_store</classname> class usage</title>\n"
"         <programlisting>\n"
"      store = POW.X509Store()\n"
"\n"
"      caFile = open( 'test/cacert.pem', 'r' )\n"
"      ca = POW.pemRead( POW.X509_CERTIFICATE, caFile.read() )\n"
"      caFile.close()\n"
"\n"
"      store.addTrust( ca )\n"
"\n"
"      certFile = open( 'test/foocom.cert', 'r' )\n"
"      x509 = POW.pemRead( POW.X509_CERTIFICATE, certFile.read() )\n"
"      certFile.close()\n"
"\n"
"      print x509.pprint()\n"
"      \n"
"      if store.verify( x509 ):\n"
"         print 'Verified certificate!.'\n"
"      else:\n"
"         print 'Failed to verify certificate!.'\n"
"         </programlisting>\n"
"      </example>\n"
"   </body>\n"
"</class>\n"
;

static PyTypeObject x509_storetype = {
	PyObject_HEAD_INIT(0)
	0,				                              /*ob_size*/
	"X509Store",		                        /*tp_name*/
	sizeof(x509_store_object),	               /*tp_basicsize*/
	0,				                              /*tp_itemsize*/
	(destructor)x509_store_object_dealloc,	   /*tp_dealloc*/
	(printfunc)0,		                        /*tp_print*/
	(getattrfunc)x509_store_object_getattr,	/*tp_getattr*/
	(setattrfunc)0,	                        /*tp_setattr*/
	(cmpfunc)0,		                           /*tp_compare*/
	(reprfunc)0,      		                  /*tp_repr*/
	0,			                                 /*tp_as_number*/
	0,		                                    /*tp_as_sequence*/
	0,		                                    /*tp_as_mapping*/
	(hashfunc)0,		                        /*tp_hash*/
	(ternaryfunc)0,		                     /*tp_call*/
	(reprfunc)0,		                        /*tp_str*/
	0,
   0,
   0,
   0,
	x509_storetype__doc__                    /* Documentation string */
};
/*========== x509 store Code ==========*/

/*========== x509 crl Code ==========*/
static x509_crl_object *
x509_crl_object_new(void)
{
   x509_crl_object *self=NULL;

   self = PyObject_New( x509_crl_object, &x509_crltype );
   if (self == NULL)
      goto error;

   self->crl = X509_CRL_new();

   return self;

error:

   Py_XDECREF(self);
   return NULL;
}

static x509_crl_object *
x509_crl_object_pem_read(BIO *in)
{
   x509_crl_object *self;

   self = PyObject_New( x509_crl_object, &x509_crltype );
   if (self == NULL)
      goto error;

   if( !(self->crl = PEM_read_bio_X509_CRL( in, NULL, NULL, NULL ) ) )
      { PyErr_SetString( SSLErrorObject, "could not load certificate" ); goto error; }

   return self;

error:

   Py_XDECREF(self);
   return NULL;
}

static x509_crl_object *
x509_crl_object_der_read(char *src, int len)
{
   x509_crl_object *self;
   unsigned char* ptr = src;

   if ( !(self = PyObject_New( x509_crl_object, &x509_crltype ) ) )
      goto error;

   self->crl = X509_CRL_new();

   if( !(d2i_X509_CRL( &self->crl, &ptr, len ) ) )
      { PyErr_SetString( SSLErrorObject, "could not load PEM encoded CRL" ); goto error; }

   return self;

error:

   Py_XDECREF(self);
   return NULL;
}

static char x509_crl_object_get_version__doc__[] = 
"<method>\n"
"   <header>\n"
"      <memberof>X509Crl</memberof>\n"
"      <name>getVersion</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method returns the version number from the version field of\n"
"         this CRL. \n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
x509_crl_object_get_version(x509_crl_object *self, PyObject *args)
{
   long version=0;

	if (!PyArg_ParseTuple(args, ""))
		goto error;

   if ( (version = ASN1_INTEGER_get( self->crl->crl->version ) ) == -1 )
      { PyErr_SetString( SSLErrorObject, "could not get crl version" ); goto error; }

   return Py_BuildValue("l", version);

error:

   return NULL;
}

static char x509_crl_object_set_version__doc__[] = 
"<method>\n"
"   <header>\n"
"      <memberof>X509Crl</memberof>\n"
"      <name>setVersion</name>\n"
"      <parameter>version</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method sets the version number in the version field of\n"
"         this CRL.  <parameter>version</parameter> should be an\n"
"         integer.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
x509_crl_object_set_version(x509_crl_object *self, PyObject *args)
{
   long version=0;
   ASN1_INTEGER *asn1_version=NULL;

	if (!PyArg_ParseTuple(args, "i", &version))
		goto error;

   if ( !(asn1_version = ASN1_INTEGER_new() ) )
      { PyErr_SetString( SSLErrorObject, "could not allocate memory" ); goto error; }

   if ( !ASN1_INTEGER_set( asn1_version, version ) )
      { PyErr_SetString( SSLErrorObject, "could not get set version" ); goto error; }

   self->crl->crl->version = asn1_version;

   return Py_BuildValue("");

error:

   if (asn1_version)
      ASN1_INTEGER_free(asn1_version);

   return NULL;
}

static char x509_crl_object_get_issuer__doc__[] = 
"<method>\n"
"   <header>\n"
"      <memberof>X509Crl</memberof>\n"
"      <name>getIssuer</name>\n"
"      <parameter>format=SHORTNAME_FORMAT</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method returns a tuple containing the issuers name.  See the\n"
"         <function>getIssuer</function> method of\n"
"         <classname>X509</classname> for more details.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
x509_crl_object_get_issuer(x509_crl_object *self, PyObject *args)
{
   PyObject *result_list = NULL;
   int format=SHORTNAME_FORMAT;

	if (!PyArg_ParseTuple(args, "|i", &format))
		goto error;

   if ( !(result_list = X509_object_helper_get_name(self->crl->crl->issuer, format) ) )
      { PyErr_SetString( SSLErrorObject, "failed to produce name list" ); goto error; }

   return result_list;

error:

   return NULL;
}

static char x509_crl_object_set_issuer__doc__[] = 
"<method>\n"
"   <header>\n"
"      <memberof>X509Crl</memberof>\n"
"      <name>setIssuer</name>\n"
"      <parameter>name</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method is used to set the issuers name.\n"
"         <parameter>name</parameter> can be comprised of lists or tuples in\n"
"         the format described in the <function>getIssuer</function> method\n"
"         of <classname>X509</classname>.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
x509_crl_object_set_issuer(x509_crl_object *self, PyObject *args)
{
   PyObject *name_sequence = NULL;
   X509_NAME *name = NULL;

	if (!PyArg_ParseTuple(args, "O", &name_sequence))
		goto error;

   if ( !( PyTuple_Check( name_sequence ) || PyList_Check(name_sequence) ) )
      { PyErr_SetString( PyExc_TypeError, "Inapropriate type" ); goto error; }

   if ( !(name = X509_NAME_new() ) )
      { PyErr_SetString( SSLErrorObject, "could not allocate memory" ); goto error; }

   if ( !X509_object_helper_set_name(name, name_sequence) )
      { PyErr_SetString( SSLErrorObject, "unable to set new name" ); goto error; }

	if ( !X509_NAME_set(&self->crl->crl->issuer,name ) )
      { PyErr_SetString( SSLErrorObject, "unable to set name" ); goto error; }

   X509_NAME_free(name);

   return Py_BuildValue("");

error:

   if (name)
      X509_NAME_free(name);

   return  NULL;
}

static char x509_crl_object_set_this_update__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>X509Crl</memberof>\n"
"      <name>setThisUpdate</name>\n"
"      <parameter>time</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         In a change from previous releases, for reasons of portability\n"
"         and to avoid hard to fix issues with problems in unreliable time\n"
"         functions, this accepts one parameter, a UTCTime string.  You\n"
"         can use the function <function>time2utc</function> to convert to a\n"
"         string if you like and <function>utc2time</function> to back.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
x509_crl_object_set_this_update (x509_crl_object *self, PyObject *args)
{
   //int new_time = 0;
   char *new_time=NULL;

	if (!PyArg_ParseTuple(args, "s", &new_time))
		goto error;

	if ( !ASN1_UTCTIME_set_string(self->crl->crl->lastUpdate,new_time) )
      { PyErr_SetString( SSLErrorObject, "could not set time" ); goto error; }

   return Py_BuildValue("");

error:

   return NULL;
}

static char x509_crl_object_get_this_update__doc__[] = 
"<method>\n"
"   <header>\n"
"      <memberof>X509Crl</memberof>\n"
"      <name>getThisUpdate</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         In a change from previous releases, for reasons of portability\n"
"         and to avoid hard to fix issues with problems in unreliable time\n"
"         functions, this function returns a UTCTime string.  You\n"
"         can use the function <function>time2utc</function> to convert to a\n"
"         string if you like and <function>utc2time</function> to back.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
x509_crl_object_get_this_update (x509_crl_object *self, PyObject *args)
{
	if (!PyArg_ParseTuple(args, ""))
		goto error;

   return Py_BuildValue("s", self->crl->crl->lastUpdate->data);

error:

   return NULL;
}

static char x509_crl_object_set_next_update__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>X509Crl</memberof>\n"
"      <name>setNextUpdate</name>\n"
"      <parameter>time</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         In a change from previous releases, for reasons of portability\n"
"         and to avoid hard to fix issues with problems in unreliable time\n"
"         functions, this accepts one parameter, a UTCTime string.  You\n"
"         can use the function <function>time2utc</function> to convert to a\n"
"         string if you like and <function>utc2time</function> to back.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
x509_crl_object_set_next_update (x509_crl_object *self, PyObject *args)
{
   //int new_time = 0;
   char *new_time=NULL;
   ASN1_UTCTIME *time=NULL;

	if (!PyArg_ParseTuple(args, "s", &new_time))
		goto error;

   if (self->crl->crl->nextUpdate == NULL)
      if ( !(time = ASN1_UTCTIME_new() ) )
         { PyErr_SetString( SSLErrorObject, "could not allocate memory" ); goto error; }

	self->crl->crl->nextUpdate = time;

	if (!ASN1_UTCTIME_set_string(time, new_time) )
      { PyErr_SetString( SSLErrorObject, "could not set next update" ); goto error; }


   return Py_BuildValue("");

error:

   return NULL;
}

static char x509_crl_object_get_next_update__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>X509Crl</memberof>\n"
"      <name>getNextUpdate</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         In a change from previous releases, for reasons of portability\n"
"         and to avoid hard to fix issues with problems in unreliable time\n"
"         functions, this function returns a UTCTime string.  You\n"
"         can use the function <function>time2utc</function> to convert to a\n"
"         string if you like and <function>utc2time</function> to back.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
x509_crl_object_get_next_update (x509_crl_object *self, PyObject *args)
{
	if (!PyArg_ParseTuple(args, ""))
		goto error;

   return Py_BuildValue("s", self->crl->crl->nextUpdate->data);

error:

   return NULL;
}

static char x509_crl_object_set_revoked__doc__[] = 
"<method>\n"
"   <header>\n"
"      <memberof>X509Crl</memberof>\n"
"      <name>setRevoked</name>\n"
"      <parameter>revoked</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method sets the sequence of revoked certificates in this CRL.\n"
"         <parameter>revoked</parameter> should be a list or tuple of \n"
"         <classname>X509Revoked</classname>.\n"
"      </para>\n"
"      <example>\n"
"         <title><function>setRevoked</function> function usage</title>\n"
"         <programlisting>\n"
"      privateFile = open('test/private.key', 'r')\n"
"      publicFile = open('test/public.key', 'r')\n"
"      crlFile = open('test/crl.pem', 'w')\n"
"\n"
"      publicKey = POW.pemRead(POW.RSA_PUBLIC_KEY, publicFile.read())\n"
"      privateKey = POW.pemRead(POW.RSA_PRIVATE_KEY, privateFile.read(), 'pass')\n"
"\n"
"      crl = POW.X509Crl()\n"
"\n"
"      name = [  ['C', 'GB'], ['ST', 'Hertfordshire'], \n"
"                ['O','The House'], ['CN', 'Peter Shannon'] ]\n"
"\n"
"      t1 = POW.pkix.time2utc( time.time() )     \n"
"      t2 = POW.pkix.time2utc( time.time() + 60*60*24*365)     \n"
"      crl.setIssuer( name )\n"
"      rev = [  POW.X509Revoked(3, t1),\n"
"               POW.X509Revoked(4, t1),\n"
"               POW.X509Revoked(5, t1)    ]\n"
"\n"
"      crl.setRevoked( rev )\n"
"      crl.setThisUpdate(t1)\n"
"      crl.setNextUpdate(t2)\n"
"      crl.sign(privateKey)\n"
"\n"
"      crlFile.write( crl.pemWrite() )\n"
"\n"
"      privateFile.close()\n"
"      publicFile.close()\n"
"      crlFile.close()\n"
"         </programlisting>\n"
"      </example>\n"
"\n"
"   </body>\n"
"</method>\n"
;

// added because we don't already have one!
static X509_REVOKED *
X509_REVOKED_dup(X509_REVOKED *rev)
{
   return((X509_REVOKED *)ASN1_dup((int (*)())i2d_X509_REVOKED,
      (char *(*)())d2i_X509_REVOKED,(char *)rev));
}

static PyObject *
x509_crl_object_set_revoked(x509_crl_object *self, PyObject *args)
{
   PyObject *revoked_sequence = NULL;
   x509_revoked_object *revoked = NULL;
   STACK_OF(X509_REVOKED) *revoked_stack = NULL;
   X509_REVOKED *tmp_revoked = NULL;
   int i=0,size=0;

	if (!PyArg_ParseTuple(args, "O", &revoked_sequence))
		goto error;

   if ( !( PyTuple_Check( revoked_sequence ) || PyList_Check(revoked_sequence) ) )
      { PyErr_SetString( PyExc_TypeError, "inapropriate type" ); goto error; }

   revoked_stack = self->crl->crl->revoked;

   size = PySequence_Size( revoked_sequence );
   for (i=0; i < size; i++)
   {
      if ( !( revoked = (x509_revoked_object*)PySequence_GetItem( revoked_sequence, i ) ) )
         goto error;

      if ( !X_X509_revoked_Check( revoked ) )
         { PyErr_SetString( PyExc_TypeError, "inapropriate type" ); goto error; }

      if ( !(tmp_revoked = X509_REVOKED_dup( revoked->revoked ) ) )
         { PyErr_SetString( SSLErrorObject, "could not allocate memory" ); goto error; }

      if (!sk_X509_REVOKED_push( revoked_stack, tmp_revoked ) )
         { PyErr_SetString( SSLErrorObject, "could not add revokation to stack" ); goto error; }

      Py_DECREF(revoked);
      revoked = NULL;
   }

   return Py_BuildValue("");

error:

   Py_XDECREF(revoked);

   return  NULL;
}

static PyObject *
x509_crl_object_helper_get_revoked(STACK_OF(X509_REVOKED) *revoked)
{
   int no_entries=0, inlist=0, i=0;
   X509_REVOKED *revoke_tmp=NULL;
   x509_revoked_object *revoke_obj=NULL;
   PyObject *item=NULL, *result_list=NULL, *result_tuple=NULL;

   no_entries = sk_X509_REVOKED_num( revoked );

   if ( !(result_list = PyList_New(0) ) )
      { PyErr_SetString( SSLErrorObject, "could not allocate memory" ); goto error; }

   for(i=0; i<no_entries; i++)
   {
      if ( !(revoke_obj = PyObject_New( x509_revoked_object, &x509_revokedtype ) ) )
         { PyErr_SetString( SSLErrorObject, "could not allocate memory" ); goto error; }

      if ( !(revoke_tmp = sk_X509_REVOKED_value( revoked, i ) ) )
         { PyErr_SetString( SSLErrorObject, "could not get revocation" ); goto error; }

      revoke_obj->revoked = revoke_tmp;

      if ( PyList_Append( result_list, (PyObject*)revoke_obj ) != 0)
         goto error;

      revoke_obj = NULL; revoke_tmp = NULL;
   }

	result_tuple = PyList_AsTuple( result_list );
   Py_DECREF(result_list);
 
   return Py_BuildValue("O", result_tuple);

error:

   if (result_list)
   {
      inlist = PyList_Size( result_list );
      for (i=0; i < inlist; i++)
      {
         item = PyList_GetItem( result_list, i );
         Py_DECREF(item);
      }
      Py_DECREF(result_list);
   }

   return NULL;
}

static char x509_crl_object_get_revoked__doc__[] = 
"<method>\n"
"   <header>\n"
"      <memberof>X509Crl</memberof>\n"
"      <name>getRevoked</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method returns a tuple of <classname>X509Revoked</classname>\n"
"         objects described in the CRL.\n"
"      </para>\n"
"      <example>\n"
"         <title><function>getRevoked</function> function usage</title>\n"
"         <programlisting>\n"
"      publicFile = open('test/public.key', 'r')\n"
"      crlFile = open('test/crl.pem', 'r')\n"
"\n"
"      publicKey = POW.pemRead(POW.RSA_PUBLIC_KEY, publicFile.read())\n"
"\n"
"      crl = POW.pemRead( POW.X509_CRL, crlFile.read() )\n"
"\n"
"      print crl.pprint()\n"
"      if crl.verify( publicKey ):\n"
"         print 'signature ok!'\n"
"      else:\n"
"         print 'signature not ok!'\n"
"\n"
"      revocations = crl.getRevoked()\n"
"      for revoked in revocations:\n"
"         print 'serial number:', revoked.getSerial()\n"
"         print 'date:', time.ctime( revoked.getDate()[0] )\n"
"\n"
"      publicFile.close()\n"
"      crlFile.close()\n"
"         </programlisting>\n"
"      </example>\n"
"\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
x509_crl_object_get_revoked(x509_crl_object *self, PyObject *args)
{
   PyObject *revoked = NULL;

	if (!PyArg_ParseTuple(args, ""))
		goto error;

   revoked = x509_crl_object_helper_get_revoked( X509_CRL_get_REVOKED(self->crl) );

   return revoked;

error:

   return  NULL;
}

static char X509_crl_object_add_extension__doc__[] = 
"<method>\n"
"   <header>\n"
"      <memberof>X509Crl</memberof>\n"
"      <name>addExtension</name>\n"
"      <parameter>extensionName</parameter>\n"
"      <parameter>critical</parameter>\n"
"      <parameter>extensionValue</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method adds an extension to this CRL.\n"
"         <parameter>extensionName</parameter> should be the of the\n"
"         extension.  <parameter>critical</parameter> should an integer, 1\n"
"         for true and 0 for clase.  <parameter>extensionValue</parameter>\n"
"         should be a string, DER encoded value of the extension.  The name\n"
"         of the extension must be correct according to OpenSSL and can be\n"
"         checkd in the <constant>objects.h</constant> header file, part of\n"
"         the OpenSSL source distrobution.  In the majority of cases they\n"
"         are the same as those defined in <constant>POW._oids</constant>\n"
"         but if you do encounter problems is may be worth checking.\n"
"      </para>\n"
"      <example>\n"
"         <title><function>addExtension</function> method usage</title>\n"
"         <programlisting>\n"
"      oids = POW.pkix.OidData()\n"
"      o2i = oids.obj2oid\n"
"\n"
"      n1 = ('directoryName',  (  (( o2i('countryName'), ('printableString', 'UK') ),), \n"
"                                 (( o2i('stateOrProvinceName'), ('printableString', 'Herts') ),), \n"
"                                 (( o2i('organizationName'), ('printableString', 'The House') ),),\n"
"                                 (( o2i('commonName'), ('printableString', 'Shannon Works') ),) ) ) \n"
"\n"
"      n2 = ('rfc822Name', 'peter_shannon@yahoo.com')\n"
"      n3 = ('uri', 'http://www.p-s.org.uk') \n"
"      n4 = ('iPAddress', (192,168,100,51)) \n"
"\n"
"      issuer = POW.pkix.IssuerAltName()\n"
"      issuer.set([n1,n2,n3,n4]) \n"
"      crl.addExtension( 'issuerAltName', 0, issuer.toString() )\n"
"         </programlisting>\n"
"      </example>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
X509_crl_object_add_extension(x509_crl_object *self, PyObject *args)
{
   int critical=0, nid=0;
   char *name=NULL, *buf=NULL;
   ASN1_OCTET_STRING *octetString=NULL;
   X509_EXTENSION *extn=NULL;

	if (!PyArg_ParseTuple(args, "sis", &name, &critical, &buf))
		goto error;

   if ( !(octetString = M_ASN1_OCTET_STRING_new() ) )
      { PyErr_SetString( SSLErrorObject, "could not allocate memory" ); goto error; }

   if ( !ASN1_OCTET_STRING_set(octetString, buf, strlen(buf)) )
      { PyErr_SetString( SSLErrorObject, "could not set ASN1 Octect string" ); goto error; }

   if ( NID_undef == (nid = OBJ_txt2nid(name) ) )
      { PyErr_SetString( SSLErrorObject, "extension has unknown object identifier" ); goto error; }

   if ( !( extn = X509_EXTENSION_create_by_NID(NULL, nid, critical, octetString) ) )
      { PyErr_SetString( SSLErrorObject, "unable to create ASN1 X509 Extension object" ); goto error; }

   if (!self->crl->crl->extensions)
      if ( !(self->crl->crl->extensions = sk_X509_EXTENSION_new_null() ) ) 
         { PyErr_SetString( SSLErrorObject, "unable to allocate memory" ); goto error; }

   if ( !sk_X509_EXTENSION_push(self->crl->crl->extensions, extn) )
      { PyErr_SetString( SSLErrorObject, "unable to add extension" ); goto error; }

   return Py_BuildValue("");

error:

   if(extn)
      X509_EXTENSION_free(extn);
 
   return NULL;
}

static char X509_crl_object_clear_extensions__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>X509Crl</memberof>\n"
"      <name>clearExtensions</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method clears the structure which holds the extension for\n"
"         this CRL.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
X509_crl_object_clear_extensions(x509_crl_object *self, PyObject *args)
{
	if (!PyArg_ParseTuple(args, ""))
		goto error;

   if (self->crl->crl->extensions)
   {
      sk_X509_EXTENSION_free(self->crl->crl->extensions);
      self->crl->crl->extensions=NULL;
   }

   return Py_BuildValue("");

error:

   return NULL;
}

static char X509_crl_object_count_extensions__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>X509Crl</memberof>\n"
"      <name>countExtensions</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method returns the size of the structure which holds the\n"
"         extension for this CRL.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
X509_crl_object_count_extensions(x509_crl_object *self, PyObject *args)
{
   int num=0;
	if (!PyArg_ParseTuple(args, ""))
		goto error;

   if (self->crl->crl->extensions)
   {
      num = sk_X509_EXTENSION_num(self->crl->crl->extensions);
      return Py_BuildValue("i", num);
   }
   else
      return Py_BuildValue("i", 0);

error:

   return NULL;
}

static char X509_crl_object_get_extension__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>X509Crl</memberof>\n"
"      <name>getExtension</name>\n"
"      <parameter>index</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method returns a tuple equivalent the parameters of\n"
"         <function>addExtension</function>.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
X509_crl_object_get_extension(x509_crl_object *self, PyObject *args)
{
   int num=0, index=0, ext_nid=0;
   char const *ext_ln=NULL;
   char unknown_ext [] = "unkown";
   X509_EXTENSION *ext;
	if (!PyArg_ParseTuple(args, "i", &index))
		goto error;

   if (self->crl->crl->extensions)
   {
      num = sk_X509_EXTENSION_num(self->crl->crl->extensions);
   }
   else
      num = 0;

   if (index >= num)
      { PyErr_SetString( SSLErrorObject, "certificate does not have that many extensions" ); goto error; }

   if ( !(ext = sk_X509_EXTENSION_value(self->crl->crl->extensions, index) ) )
      { PyErr_SetString( SSLErrorObject, "could not get extension" ); goto error; }

   if ( NID_undef == (ext_nid = OBJ_obj2nid(ext->object) ) )
      { PyErr_SetString( SSLErrorObject, "extension has unknown object identifier" ); goto error; }

   if ( NULL == (ext_ln = OBJ_nid2sn(ext_nid) ) )
      ext_ln = unknown_ext;

   return Py_BuildValue("sis", ext_ln, ext->critical, ext->value->data );

error:

   return NULL;
}

static char x509_crl_object_sign__doc__[] = 
"<method>\n"
"   <header>\n"
"      <memberof>X509Crl</memberof>\n"
"      <name>sign</name>\n"
"      <parameter>key</parameter>\n"
"      <parameter>digest=MD5_DIGEST</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         <parameter>key</parameter> should be an instance of\n"
"         <classname>Asymmetric</classname> and contain a private key.\n"
"         <parameter>digest</parameter> indicates \n"
"         which digest function should be used to compute the hash to be \n"
"         signed, it should be one of the following:\n"
"      </para>\n"
"      <simplelist>\n"
"         <member><constant>MD2_DIGEST</constant></member>\n"
"         <member><constant>MD5_DIGEST</constant></member>\n"
"         <member><constant>SHA_DIGEST</constant></member>\n"
"         <member><constant>SHA1_DIGEST</constant></member>\n"
"         <member><constant>RIPEMD160_DIGEST</constant></member>\n"
"     </simplelist>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
x509_crl_object_sign(x509_crl_object *self, PyObject *args)
{
	EVP_PKEY *pkey=NULL;
   asymmetric_object *asym;
   int digest=MD5_DIGEST;

	if (!PyArg_ParseTuple(args, "O!|i", &asymmetrictype, &asym, &digest))
		goto error;

   if ( !(pkey = EVP_PKEY_new() ) )
      { PyErr_SetString( SSLErrorObject, "could not allocate memory" ); goto error; }

   if (asym->key_type != RSA_PRIVATE_KEY)
      { PyErr_SetString( SSLErrorObject, "cannot use this type of key" ); goto error; }

   if ( !(EVP_PKEY_assign_RSA(pkey, asym->cipher) ) )
      { PyErr_SetString( SSLErrorObject, "EVP_PKEY assignment error" ); goto error; }

   switch (digest)
   {
      case MD5_DIGEST:
      { 
         if (!X509_CRL_sign(self->crl, pkey, EVP_md5() ) ) 
            { PyErr_SetString( SSLErrorObject, "could not sign certificate" ); goto error; }
         break;
      }
      case MD2_DIGEST:
      { 
         if (!X509_CRL_sign(self->crl, pkey, EVP_md2() ) ) 
            { PyErr_SetString( SSLErrorObject, "could not sign certificate" ); goto error; }
         break;
      }
      case SHA_DIGEST:
      { 
         if (!X509_CRL_sign(self->crl, pkey, EVP_sha() ) ) 
            { PyErr_SetString( SSLErrorObject, "could not sign certificate" ); goto error; }
         break;
      }
      case SHA1_DIGEST:
      { 
         if (!X509_CRL_sign(self->crl, pkey, EVP_sha1() ) ) 
            { PyErr_SetString( SSLErrorObject, "could not sign certificate" ); goto error; }
         break;
      }
      case RIPEMD160_DIGEST:
      { 
         if (!X509_CRL_sign(self->crl, pkey, EVP_ripemd160() ) ) 
            { PyErr_SetString( SSLErrorObject, "could not sign certificate" ); goto error; }
         break;
      }
   }

   return Py_BuildValue("");

error:

   if (pkey)
      EVP_PKEY_free(pkey);

   return NULL;

}

static char x509_crl_object_verify__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>X509Crl</memberof>\n"
"      <name>verify</name>\n"
"      <parameter>key</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         The <classname>X509Crl</classname> method\n"
"         <function>verify</function> is based on the\n"
"         <function>X509_CRL_verify</function> function.  Unlike the\n"
"         <classname>X509</classname> function of the same name, this\n"
"         function simply checks the CRL was signed with the private key\n"
"         which corresponds the parameter <parameter>key</parameter>.\n"
"         <parameter>key</parameter> should be an instance of\n"
"         <classname>Asymmetric</classname> and contain a public key.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
x509_crl_object_verify(x509_crl_object *self, PyObject *args)
{
   int result=0;
	EVP_PKEY *pkey=NULL;
   asymmetric_object *asym;

	if (!PyArg_ParseTuple(args, "O!", &asymmetrictype, &asym))
		goto error;

   if ( !(pkey = EVP_PKEY_new() ) )
      { PyErr_SetString( SSLErrorObject, "could not allocate memory" ); goto error; }

   if ( !(EVP_PKEY_assign_RSA(pkey, asym->cipher) ) )
      { PyErr_SetString( SSLErrorObject, "EVP_PKEY assignment error" ); goto error; }

	result = X509_CRL_verify(self->crl,pkey);

   return Py_BuildValue("i", result);

error:

   if (pkey)
      EVP_PKEY_free(pkey);

   return NULL;

}

static PyObject *
x509_crl_object_write_helper(x509_crl_object *self, PyObject *args, int format)
{
   int len=0, ret=0;
   char *buf=NULL;
   BIO *out_bio=NULL;
   PyObject *cert=NULL;
   
	if (!PyArg_ParseTuple(args, ""))
		goto error;

   out_bio = BIO_new(BIO_s_mem());

   if (format == DER_FORMAT)
   {
      if (!i2d_X509_CRL_bio(out_bio, self->crl) )
         { PyErr_SetString( SSLErrorObject, "unable to write certificate" ); goto error; }
   }
   else if (format == PEM_FORMAT)
   {
      if (!PEM_write_bio_X509_CRL(out_bio, self->crl) )
         { PyErr_SetString( SSLErrorObject, "unable to write certificate" ); goto error; }
   }
   else
      { PyErr_SetString( SSLErrorObject, "internal error, unkown output format" ); goto error; }

   if ( !(len = BIO_ctrl_pending(out_bio) ) )
      { PyErr_SetString( SSLErrorObject, "unable to get bytes stored in bio" ); goto error; }

   if ( !(buf = malloc(len) ) )
      { PyErr_SetString( SSLErrorObject, "unable to allocate memory" ); goto error; }

   if ( (ret = BIO_read( out_bio, buf, len ) ) != len )
      { PyErr_SetString( SSLErrorObject, "unable to write out cert" ); goto error; }

   cert = Py_BuildValue("s#", buf, len);

   BIO_free(out_bio);
   free(buf);
   return cert;
   
error:   

   if (out_bio)
      BIO_free(out_bio);

   if (buf)
      free(buf);

   return NULL;
}

static char x509_crl_object_pem_write__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>X509Crl</memberof>\n"
"      <name>pemWrite</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method returns a PEM encoded CRL as a\n"
"         string.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
x509_crl_object_pem_write(x509_crl_object *self, PyObject *args)
{
   return x509_crl_object_write_helper(self, args, PEM_FORMAT);
}

static char x509_crl_object_der_write__doc__[] = 
"<method>\n"
"   <header>\n"
"      <memberof>X509Crl</memberof>\n"
"      <name>derWrite</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method returns a DER encoded CRL as a string.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
x509_crl_object_der_write(x509_crl_object *self, PyObject *args)
{
   return x509_crl_object_write_helper(self, args, DER_FORMAT);
}

static char x509_crl_object_pprint__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>X509Crl</memberof>\n"
"      <name>pprint</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method returns a formatted string showing the information\n"
"         held in the CRL.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
x509_crl_object_pprint(x509_crl_object *self, PyObject *args)
{
   int len=0, ret=0;
   char *buf=NULL;
   BIO *out_bio=NULL;
   PyObject *crl=NULL;
   
	if (!PyArg_ParseTuple(args, ""))
		goto error;

   out_bio = BIO_new(BIO_s_mem());

   if (!X509_CRL_print(out_bio, self->crl) )
      { PyErr_SetString( SSLErrorObject, "unable to write crl" ); goto error; }

   if ( !(len = BIO_ctrl_pending(out_bio) ) )
      { PyErr_SetString( SSLErrorObject, "unable to get bytes stored in bio" ); goto error; }

   if ( !(buf = malloc(len) ) )
      { PyErr_SetString( SSLErrorObject, "unable to allocate memory" ); goto error; }

   if ( (ret = BIO_read( out_bio, buf, len ) ) != len )
      { PyErr_SetString( SSLErrorObject, "unable to write out cert" ); goto error; }

   crl = Py_BuildValue("s#", buf, len);

   BIO_free(out_bio);
   free(buf);
   return crl;
   
error:   

   if (out_bio)
      BIO_free(out_bio);

   if (buf)
      free(buf);

   return NULL;

}

static struct PyMethodDef x509_crl_object_methods[] = {
   {"sign",          (PyCFunction)x509_crl_object_sign,              METH_VARARGS,  NULL}, 
   {"verify",        (PyCFunction)x509_crl_object_verify,            METH_VARARGS,  NULL}, 
   {"getVersion",    (PyCFunction)x509_crl_object_get_version,       METH_VARARGS,  NULL}, 
   {"setVersion",    (PyCFunction)x509_crl_object_set_version,       METH_VARARGS,  NULL}, 
   {"getIssuer",     (PyCFunction)x509_crl_object_get_issuer,        METH_VARARGS,  NULL}, 
   {"setIssuer",     (PyCFunction)x509_crl_object_set_issuer,        METH_VARARGS,  NULL}, 
   {"getThisUpdate", (PyCFunction)x509_crl_object_get_this_update,   METH_VARARGS,  NULL}, 
   {"setThisUpdate", (PyCFunction)x509_crl_object_set_this_update,   METH_VARARGS,  NULL}, 
   {"getNextUpdate", (PyCFunction)x509_crl_object_get_next_update,   METH_VARARGS,  NULL}, 
   {"setNextUpdate", (PyCFunction)x509_crl_object_set_next_update,   METH_VARARGS,  NULL}, 
   {"setRevoked",    (PyCFunction)x509_crl_object_set_revoked,       METH_VARARGS,  NULL}, 
   {"getRevoked",    (PyCFunction)x509_crl_object_get_revoked,       METH_VARARGS,  NULL}, 
   {"addExtension",  (PyCFunction)X509_crl_object_add_extension,     METH_VARARGS,  NULL}, 
   {"clearExtensions",(PyCFunction)X509_crl_object_clear_extensions, METH_VARARGS,  NULL}, 
   {"countExtensions",(PyCFunction)X509_crl_object_count_extensions, METH_VARARGS,  NULL}, 
   {"getExtension",  (PyCFunction)X509_crl_object_get_extension,     METH_VARARGS,  NULL}, 
   {"pemWrite",      (PyCFunction)x509_crl_object_pem_write,         METH_VARARGS,  NULL}, 
   {"derWrite",      (PyCFunction)x509_crl_object_der_write,         METH_VARARGS,  NULL}, 
   {"pprint",        (PyCFunction)x509_crl_object_pprint,            METH_VARARGS,  NULL}, 
 
	{NULL,		NULL}		/* sentinel */
};

static PyObject *
x509_crl_object_getattr(x509_crl_object *self, char *name)
{
	return Py_FindMethod(x509_crl_object_methods, (PyObject *)self, name);
}

static void
x509_crl_object_dealloc(x509_crl_object *self, char *name)
{
   X509_CRL_free( self->crl );
   PyObject_Del(self);
}

static char x509_crltype__doc__[] =
"<class>\n"
"   <header>\n"
"      <name>X509Crl</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This class provides access to OpenSSL X509 CRL management\n"
"         facilities.\n"
"      </para>\n"
"   </body>\n"
"</class>\n"
;

static PyTypeObject x509_crltype = {
	PyObject_HEAD_INIT(0)
	0,				                           /*ob_size*/
	"X509Crl",		                        /*tp_name*/
	sizeof(x509_crl_object),	            /*tp_basicsize*/
	0,				                           /*tp_itemsize*/
	(destructor)x509_crl_object_dealloc,	/*tp_dealloc*/
	(printfunc)0,		                     /*tp_print*/
	(getattrfunc)x509_crl_object_getattr,	/*tp_getattr*/
	(setattrfunc)0,	                     /*tp_setattr*/
	(cmpfunc)0,		                        /*tp_compare*/
	(reprfunc)0,      		               /*tp_repr*/
	0,			                              /*tp_as_number*/
	0,		                                 /*tp_as_sequence*/
	0,		                                 /*tp_as_mapping*/
	(hashfunc)0,		                     /*tp_hash*/
	(ternaryfunc)0,		                  /*tp_call*/
	(reprfunc)0,		                     /*tp_str*/
	0,
   0,
   0,
   0,
	x509_crltype__doc__                   /* Documentation string */
};
/*========== x509 crl Code ==========*/

/*========== revoked Code ==========*/
x509_revoked_object* x509_revoked_object_new(void)
{
   x509_revoked_object *self=NULL;

   if ( !(self = PyObject_New( x509_revoked_object, &x509_revokedtype ) ) )
      goto error;

   self->revoked = X509_REVOKED_new();

   return self;

error:

   Py_XDECREF(self);
   return NULL;
}

static char x509_revoked_object_set_serial__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>X509Revoked</memberof>\n"
"      <name>setSerial</name>\n"
"      <parameter>serial</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method sets the serial number in the serial field of\n"
"         this object.  <parameter>serial</parameter> should be an\n"
"         integer.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
x509_revoked_object_set_serial(x509_revoked_object *self, PyObject *args)
{
   int serial=0;

	if (!PyArg_ParseTuple(args, "i", &serial))
		goto error;

   if (!ASN1_INTEGER_set( self->revoked->serialNumber, serial ) )
      { PyErr_SetString( SSLErrorObject, "unable to set serial number" ); goto error; }

   return Py_BuildValue("");

error:

   return NULL;
}

static char x509_revoked_object_get_serial__doc__[] = 
"<method>\n"
"   <header>\n"
"      <memberof>X509Revoked</memberof>\n"
"      <name>getSerial</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method gets the serial number in the serial field of\n"
"         this object.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
x509_revoked_object_get_serial(x509_revoked_object *self, PyObject *args)
{
   int serial=0;

	if (!PyArg_ParseTuple(args, ""))
		goto error;

   if ( (serial = ASN1_INTEGER_get( self->revoked->serialNumber ) ) == -1 )
      { PyErr_SetString( SSLErrorObject, "unable to get serial number" ); goto error; }

   return Py_BuildValue("i", serial);

error:

   return NULL;
}

static char x509_revoked_object_get_date__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>X509Revoked</memberof>\n"
"      <name>getDate</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         In a change from previous releases, for reasons of portability\n"
"         and to avoid hard to fix issues with problems in unreliable time\n"
"         functions, this function returns a UTCTime string.  You\n"
"         can use the function <function>time2utc</function> to convert to a\n"
"         string if you like and <function>utc2time</function> to back.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
x509_revoked_object_get_date(x509_revoked_object *self, PyObject *args)
{
	if (!PyArg_ParseTuple(args, ""))
		goto error;

   return Py_BuildValue("s", self->revoked->revocationDate->data);

error:

   return NULL;
}

static char x509_revoked_object_set_date__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>X509Revoked</memberof>\n"
"      <name>setDate</name>\n"
"      <parameter>time</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         In a change from previous releases, for reasons of portability\n"
"         and to avoid hard to fix issues with problems in unreliable time\n"
"         functions, this accepts one parameter, a UTCTime string.  You\n"
"         can use the function <function>time2utc</function> to convert to a\n"
"         string if you like and <function>utc2time</function> to back.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
x509_revoked_object_set_date(x509_revoked_object *self, PyObject *args)
{
   char *time=NULL;

	if (!PyArg_ParseTuple(args, "s", &time))
		goto error;

   if (!ASN1_UTCTIME_set_string( self->revoked->revocationDate, time ))
      { PyErr_SetString( PyExc_TypeError, "could not set revocationDate" ); goto error; }

   return Py_BuildValue("");

error:

   return NULL;
}

static char X509_revoked_object_add_extension__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>X509Revoked</memberof>\n"
"      <name>addExtension</name>\n"
"      <parameter>extensionName</parameter>\n"
"      <parameter>critical</parameter>\n"
"      <parameter>extensionValue</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method adds an extension to this revocation.\n"
"         <parameter>extensionName</parameter> should be the of the\n"
"         extension.  <parameter>critical</parameter> should an integer, 1\n"
"         for true and 0 for clase.  <parameter>extensionValue</parameter>\n"
"         should be a string, DER encoded value of the extension.  The name\n"
"         of the extension must be correct according to OpenSSL and can be\n"
"         checkd in the <constant>objects.h</constant> header file, part of\n"
"         the OpenSSL source distrobution.  In the majority of cases they\n"
"         are the same as those defined in <constant>POW._oids</constant>\n"
"         but if you do encounter problems is may be worth checking.\n"
"      </para>\n"
"      <example>\n"
"         <title><function>addExtension</function> method usage</title>\n"
"         <programlisting>\n"
"      reason = POW.pkix.CrlReason()\n"
"      reason.set(1) \n"
"      revocation.addExtension( 'CRLReason', 0, reason.toString() )\n"
"         </programlisting>\n"
"      </example>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
X509_revoked_object_add_extension(x509_revoked_object *self, PyObject *args)
{
   int critical=0, nid=0;
   char *name=NULL, *buf=NULL;
   ASN1_OCTET_STRING *octetString=NULL;
   X509_EXTENSION *extn=NULL;

	if (!PyArg_ParseTuple(args, "sis", &name, &critical, &buf))
		goto error;

   if ( !(octetString = M_ASN1_OCTET_STRING_new() ) )
      { PyErr_SetString( SSLErrorObject, "could not allocate memory" ); goto error; }

   if ( !ASN1_OCTET_STRING_set(octetString, buf, strlen(buf)) )
      { PyErr_SetString( SSLErrorObject, "could not set ASN1 Octect string" ); goto error; }

   if ( NID_undef == (nid = OBJ_txt2nid(name) ) )
      { PyErr_SetString( SSLErrorObject, "extension has unknown object identifier" ); goto error; }

   if ( !( extn = X509_EXTENSION_create_by_NID(NULL, nid, critical, octetString) ) )
      { PyErr_SetString( SSLErrorObject, "unable to create ASN1 X509 Extension object" ); goto error; }

   if (!self->revoked->extensions)
      if ( !(self->revoked->extensions = sk_X509_EXTENSION_new_null() ) ) 
         { PyErr_SetString( SSLErrorObject, "unable to allocate memory" ); goto error; }

   if ( !sk_X509_EXTENSION_push(self->revoked->extensions, extn) )
      { PyErr_SetString( SSLErrorObject, "unable to add extension" ); goto error; }

   return Py_BuildValue("");

error:

   if(extn)
      X509_EXTENSION_free(extn);
 
   return NULL;
}

static char X509_revoked_object_clear_extensions__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>X509Revoked</memberof>\n"
"      <name>clearExtensions</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method clears the structure which holds the extension for\n"
"         this revocation.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
X509_revoked_object_clear_extensions(x509_revoked_object *self, PyObject *args)
{
	if (!PyArg_ParseTuple(args, ""))
		goto error;

   if (self->revoked->extensions)
   {
      sk_X509_EXTENSION_free(self->revoked->extensions);
      self->revoked->extensions=NULL;
   }

   return Py_BuildValue("");

error:

   return NULL;
}

static char X509_revoked_object_count_extensions__doc__[] = 
"<method>\n"
"   <header>\n"
"      <memberof>X509Revoked</memberof>\n"
"      <name>countExtensions</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method returns the size of the structure which holds the\n"
"         extension for this revocation.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
X509_revoked_object_count_extensions(x509_revoked_object *self, PyObject *args)
{
   int num=0;
	if (!PyArg_ParseTuple(args, ""))
		goto error;

   if (self->revoked->extensions)
   {
      num = sk_X509_EXTENSION_num(self->revoked->extensions);
      return Py_BuildValue("i", num);
   }
   else
      return Py_BuildValue("i", 0);

error:

   return NULL;
}

static char X509_revoked_object_get_extension__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>X509Revoked</memberof>\n"
"      <name>getExtension</name>\n"
"      <parameter>index</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method returns a tuple equivalent the parameters of\n"
"         <function>addExtension</function>.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
X509_revoked_object_get_extension(x509_revoked_object *self, PyObject *args)
{
   int num=0, index=0, ext_nid=0;
   char const *ext_ln=NULL;
   char unknown_ext [] = "unkown";
   X509_EXTENSION *ext;
	if (!PyArg_ParseTuple(args, "i", &index))
		goto error;

   if (self->revoked->extensions)
   {
      num = sk_X509_EXTENSION_num(self->revoked->extensions);
   }
   else
      num = 0;

   if (index >= num)
      { PyErr_SetString( SSLErrorObject, "certificate does not have that many extensions" ); goto error; }

   if ( !(ext = sk_X509_EXTENSION_value(self->revoked->extensions, index) ) )
      { PyErr_SetString( SSLErrorObject, "could not get extension" ); goto error; }

   if ( NID_undef == (ext_nid = OBJ_obj2nid(ext->object) ) )
      { PyErr_SetString( SSLErrorObject, "extension has unknown object identifier" ); goto error; }

   if ( NULL == (ext_ln = OBJ_nid2sn(ext_nid) ) )
      ext_ln = unknown_ext;

   return Py_BuildValue("sis", ext_ln, ext->critical, ext->value->data );

error:

   return NULL;
}

static struct PyMethodDef x509_revoked_object_methods[] = {
   {"getSerial",      (PyCFunction)x509_revoked_object_get_serial,   METH_VARARGS,  NULL}, 
   {"setSerial",      (PyCFunction)x509_revoked_object_set_serial,   METH_VARARGS,  NULL}, 
   {"getDate",        (PyCFunction)x509_revoked_object_get_date,     METH_VARARGS,  NULL}, 
   {"setDate",        (PyCFunction)x509_revoked_object_set_date,     METH_VARARGS,  NULL}, 
   {"addExtension",  (PyCFunction)X509_revoked_object_add_extension,     METH_VARARGS,  NULL}, 
   {"clearExtensions",(PyCFunction)X509_revoked_object_clear_extensions, METH_VARARGS,  NULL}, 
   {"countExtensions",(PyCFunction)X509_revoked_object_count_extensions, METH_VARARGS,  NULL}, 
   {"getExtension",  (PyCFunction)X509_revoked_object_get_extension,     METH_VARARGS,  NULL}, 

	{NULL,		NULL}		/* sentinel */
};

static PyObject *
x509_revoked_object_getattr(x509_revoked_object *self, char *name)
{
	return Py_FindMethod(x509_revoked_object_methods, (PyObject *)self, name);
}

static void
x509_revoked_object_dealloc(x509_revoked_object *self, char *name)
{
   X509_REVOKED_free( self->revoked );
   PyObject_Del(self);
}

static char x509_revokedtype__doc__[] = 
"<class>\n"
"   <header>\n"
"      <name>X509Revoked</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This class provides a container for details of a revoked\n"
"         certificate.  It normally would only be used in association with\n"
"         a CRL, its not much use by itself.  Indeed the only reason this\n"
"         class exists is because in the future POW is likely to be extended\n"
"         to support extensions for certificates, CRLs and revocations.\n"
"         <classname>X509Revoked</classname> existing as an object in its\n"
"         own right will make adding this support easier, while avoiding\n"
"         backwards compatibility issues.\n"
"      </para>\n"
"   </body>\n"
"</class>\n"
;

static PyTypeObject x509_revokedtype = {
	PyObject_HEAD_INIT(0)
	0,				                              /*ob_size*/
	"X509Revoked",		                        /*tp_name*/
	sizeof(x509_revoked_object),	            /*tp_basicsize*/
	0,				                              /*tp_itemsize*/
	(destructor)x509_revoked_object_dealloc,	/*tp_dealloc*/
	(printfunc)0,		                        /*tp_print*/
	(getattrfunc)x509_revoked_object_getattr,	/*tp_getattr*/
	(setattrfunc)0,	                        /*tp_setattr*/
	(cmpfunc)0,		                           /*tp_compare*/
	(reprfunc)0,      		                  /*tp_repr*/
	0,			                                 /*tp_as_number*/
	0,		                                    /*tp_as_sequence*/
	0,		                                    /*tp_as_mapping*/
	(hashfunc)0,		                        /*tp_hash*/
	(ternaryfunc)0,		                     /*tp_call*/
	(reprfunc)0,		                        /*tp_str*/
	0,
   0,
   0,
   0,
	x509_revokedtype__doc__                  /* Documentation string */
};
/*========== x509 revoked Code ==========*/

/*========== ssl Code ==========*/
static char ssl_object_use_certificate__doc__[] = 
"<method>\n"
"   <header>\n"
"      <memberof>Ssl</memberof>\n"
"      <name>useCertificate</name>\n"
"      <parameter>cert</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         The parameter <parameter>cert</parameter> must be an\n"
"         instance of the <classname>X590</classname> class and must be\n"
"         called before <function>setFd</function>.  \n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
ssl_object_use_certificate(ssl_object *self, PyObject *args)
{
   x509_object *x509=NULL;

	if (!PyArg_ParseTuple(args, "O!", &x509type, &x509))
		goto error;

   if (self->ctxset)
      { PyErr_SetString( SSLErrorObject, "cannont be called after setFd()" ); goto error; }

   if ( !SSL_CTX_use_certificate(self->ctx, x509->x509) )
      { PyErr_SetString( SSLErrorObject, "could not use certificate" ); goto error; }

   return Py_BuildValue("");

error:

   return NULL;
}

static char ssl_object_use_key__doc__[] = 
"<method>\n"
"   <header>\n"
"      <memberof>Ssl</memberof>\n"
"      <name>useKey</name>\n"
"      <parameter>key</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         The parameter <parameter>key</parameter> must be an\n"
"         instance of the <classname>Asymmetric</classname> class and\n"
"         must contain the private key.  This function cannot be called \n"
"         after <function>useKey</function>.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
ssl_object_use_key(ssl_object *self, PyObject *args)
{
   asymmetric_object *asym=NULL;
	EVP_PKEY *pkey=NULL;

	if (!PyArg_ParseTuple(args, "O!", &asymmetrictype, &asym))
		goto error;

   if (self->ctxset)
      { PyErr_SetString( SSLErrorObject, "cannont be called after setFd()" ); goto error; }

   if ( !(pkey = EVP_PKEY_new() ) )
      { PyErr_SetString( SSLErrorObject, "could not allocate memory" ); goto error; }

   if (asym->key_type != RSA_PRIVATE_KEY)
      { PyErr_SetString( SSLErrorObject, "cannot use this type of key" ); goto error; }

   if ( !EVP_PKEY_assign_RSA(pkey, asym->cipher) )
      { PyErr_SetString( SSLErrorObject, "EVP_PKEY assignment error" ); goto error; }

	if ( !SSL_CTX_use_PrivateKey(self->ctx, pkey) )
      { PyErr_SetString( SSLErrorObject, "ctx key assignment error" ); goto error; }

   return Py_BuildValue("");

error:

   if(pkey)
      EVP_PKEY_free(pkey);

   return NULL;
}

static char ssl_object_check_key__doc__[] = 
"<method>\n"
"   <header>\n"
"      <memberof>Ssl</memberof>\n"
"      <name>checkKey</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This simple method will return 1 if the public key, contained in\n"
"         the X509 certificate this <classname>Ssl</classname> instance is using,\n"
"         matches the private key this <classname>Ssl</classname> instance is using.\n"
"         Otherwise it will return 0.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
ssl_object_check_key(ssl_object *self, PyObject *args)
{
   if ( SSL_CTX_check_private_key(self->ctx) )
      return Py_BuildValue("i", 1);
   else
      return Py_BuildValue("i", 0);
}

static char ssl_object_set_fd__doc__[] = 
"<method>\n"
"   <header>\n"
"      <memberof>Ssl</memberof>\n"
"      <name>setFd</name>\n"
"      <parameter>descriptor</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This function is used to associate a file descriptor with a\n"
"         <classname>Ssl</classname> object.  The file descriptor should\n"
"         belong to an open TCP connection.  Once this function has\n"
"         been called, calling <function>useKey</function> or\n"
"         <function>useCertificate</function> will, fail rasing exceptions.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
ssl_object_set_fd(ssl_object *self, PyObject *args)
{
   int fd=0, self_index=0;
   
	if (!PyArg_ParseTuple(args, "i", &fd))
		goto error;

   if ( !(self->ssl = SSL_new( self->ctx ) ) )
      { PyErr_SetString( SSLErrorObject, "unable to create ssl sturcture" ); goto error; }

   if ( !SSL_set_fd( self->ssl, fd ) )
      { PyErr_SetString( SSLErrorObject, "unable to set file descriptor" ); goto error; }

   if ( (self_index = SSL_get_ex_new_index(0, "self_index", NULL, NULL, NULL) ) != -1 )
      SSL_set_ex_data(self->ssl, self_index, self);
   else
      { PyErr_SetString( SSLErrorObject, "unable to create ex data index" ); goto error; }

   self->ctxset = 1;

   return Py_BuildValue("");

error:

   return NULL;
}

static char ssl_object_accept__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>Ssl</memberof>\n"
"      <name>accept</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This function will attempt the SSL level accept with a\n"
"         client.  The <classname>Ssl</classname> object must have been\n"
"         created using a <constant>XXXXX_SERVER_METHOD</constant> or\n"
"         a <constant>XXXXX_METHOD</constant> and this function should only be\n"
"         called after <function>useKey</function>,\n"
"         <function>useCertificate</function> and\n"
"         <function>setFd</function> functions have been called.\n"
"      </para>\n"
"\n"
"      <example>\n"
"         <title><function>accept</function> function usage</title>\n"
"         <programlisting>\n"
"      keyFile = open( 'test/private.key', 'r' )\n"
"      certFile = open( 'test/cacert.pem', 'r' )\n"
"\n"
"      rsa = POW.pemRead( POW.RSA_PRIVATE_KEY, keyFile.read(), 'pass' )\n"
"      x509 = POW.pemRead( POW.X509_CERTIFICATE, certFile.read() )\n"
"\n"
"      keyFile.close()\n"
"      certFile.close()\n"
"\n"
"      sl = POW.Ssl( POW.SSLV23_SERVER_METHOD )\n"
"      sl.useCertificate( x509 )\n"
"      sl.useKey( rsa )\n"
"\n"
"      s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )\n"
"      s.bind( ('localhost', 1111) )\n"
"      s.listen(5)\n"
"      s2, addr = s.accept()\n"
"\n"
"      s.close()\n"
"\n"
"      sl.setFd( s2.fileno() )\n"
"      sl.accept()\n"
"      print sl.read(1024)\n"
"      sl.write('Message from server to client...')\n"
"\n"
"      s2.close()     \n"
"         </programlisting>\n"
"      </example>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
ssl_object_accept(ssl_object *self, PyObject *args)
{
   int ret=0, err=0;
   
	if (!PyArg_ParseTuple(args, ""))
		goto error;

   Py_BEGIN_ALLOW_THREADS 
   ret = SSL_accept( self->ssl );
   Py_END_ALLOW_THREADS

   if (ret <= 0) 
   {
      err = SSL_get_error( self->ssl, ret );
      PyErr_SetObject(SSLErrorObject, ssl_err_factory( err ) );
      goto error;
   }
   return Py_BuildValue("");

error:

   return NULL;
}

static char ssl_object_connect__doc__[] = 
"<method>\n"
"   <header>\n"
"      <memberof>Ssl</memberof>\n"
"      <name>connect</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This function will attempt the SSL level connection with a\n"
"         server.  The <classname>Ssl</classname> object must have been\n"
"         created using a <constant>XXXXX_CLIENT_METHOD</constant> or\n"
"         a <constant>XXXXX_METHOD</constant> and this function should only be\n"
"         called after <function>setFd</function> has already been\n"
"         called.\n"
"      </para>\n"
"\n"
"      <example>\n"
"         <title><function>connect</function> function usage</title>\n"
"         <programlisting>\n"
"      s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )\n"
"      s.connect(('localhost', 1111))\n"
"\n"
"      sl = POW.Ssl( POW.SSLV23_CLIENT_METHOD )\n"
"      sl.setFd( s.fileno() )\n"
"      sl.connect()\n"
"      sl.write('Message from client to server...')\n"
"      print sl.read(1024)\n"
"         </programlisting>\n"
"      </example>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
ssl_object_connect(ssl_object *self, PyObject *args)
{
   int ret, err=0;
   
	if (!PyArg_ParseTuple(args, ""))
		goto error;

   Py_BEGIN_ALLOW_THREADS 
   ret = SSL_connect( self->ssl );
   Py_END_ALLOW_THREADS 

   if (ret <= 0) 
   {
      err = SSL_get_error( self->ssl, ret );
      PyErr_SetObject(SSLErrorObject, ssl_err_factory( err ) );
      goto error;
   }
   return Py_BuildValue("");

error:

   return NULL;
}

static char ssl_object_write__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>Ssl</memberof>\n"
"      <name>write</name>\n"
"      <parameter>string</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method writes the <parameter>string</parameter> to the\n"
"         <classname>Ssl</classname> object, to be read by it's peer.  This\n"
"         function is analogous to the <classname>socket</classname>\n"
"         classes <function>write</function> function.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
ssl_object_write(ssl_object *self, PyObject *args)
{
   char *msg;
   int length=0, ret=0, err=0;
   
	if (!PyArg_ParseTuple(args, "s#", &msg, &length))
		goto error;
   
   Py_BEGIN_ALLOW_THREADS 
   ret = SSL_write( self->ssl, msg, length );
   Py_END_ALLOW_THREADS 

   if (ret <= 0) 
   {
      err = SSL_get_error( self->ssl, ret );
      PyErr_SetObject(SSLErrorObject, ssl_err_factory( err ) );
      goto error;
   }
   return Py_BuildValue("i", ret);

error:

   return NULL;
}

static char ssl_object_read__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>Ssl</memberof>\n"
"      <name>read</name>\n"
"      <parameter>amount=1024</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method reads up to <parameter>amount</parameter> characters from the\n"
"         <classname>Ssl</classname> object.  This\n"
"         function is analogous to the <classname>socket</classname>\n"
"         classes <function>read</function> function.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
ssl_object_read(ssl_object *self, PyObject *args)
{
   PyObject *data;
   char *msg=NULL;
   int len = 1024, ret=0, err=0;
   
	if (!PyArg_ParseTuple(args, "|i", &len))
		goto error;

   if ( !(msg = malloc(len) ) )
      { PyErr_SetString( SSLErrorObject, "unable to allocate memory" ); goto error; }

   Py_BEGIN_ALLOW_THREADS 
   ret = SSL_read( self->ssl, msg, len );
   Py_END_ALLOW_THREADS 

   if (ret <= 0) 
   {
      free(msg);
      err = SSL_get_error( self->ssl, ret );
      PyErr_SetObject(SSLErrorObject, ssl_err_factory( err ) );
      goto error;
   }
   else
      data = Py_BuildValue("s#", msg, ret);

   free(msg);
   return data;

error:

   if (msg)
      free(msg);

   return NULL;
}

static char ssl_object_peer_certificate__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>Ssl</memberof>\n"
"      <name>peerCertificate</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method returns any peer certificate presented in the initial\n"
"         SSL negotiation or <constant>None</constant>.  If a certificate is\n"
"         returned, it will be an instance of <classname>X509</classname>.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
ssl_object_peer_certificate(ssl_object *self, PyObject *args)
{
   X509 *x509=NULL;
   x509_object *x509_obj=NULL;

	if (!PyArg_ParseTuple(args, ""))
		goto error;

   if ( !(x509_obj = X509_object_new() ) )
      { PyErr_SetString( SSLErrorObject, "could not create x509 object" ); goto error; }

   x509 = SSL_get_peer_certificate( self->ssl );

   if (x509)
   {
      X509_free( x509_obj->x509 ); 

      if ( !(x509_obj->x509 = x509 ) )
         { PyErr_SetString( SSLErrorObject, "could not create x509 object" ); goto error; }
      return Py_BuildValue("O", x509_obj);
   }
   else
   {
      Py_XDECREF( x509_obj );
      return Py_BuildValue("");
   }

error:

   if (x509)
      X509_free(x509);

   Py_XDECREF( x509_obj );
   return NULL;
}

static char ssl_object_clear__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>Ssl</memberof>\n"
"      <name>clear</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method will clear the SSL session ready for\n"
"         a new SSL connection.  It will not effect the underlying socket.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
ssl_object_clear(ssl_object *self, PyObject *args)
{
	if (!PyArg_ParseTuple(args, ""))
		goto error;
   
   if (!SSL_clear( self->ssl ) )
      { PyErr_SetString( SSLErrorObject, "failed to clear ssl connection" ); goto error; }

   return Py_BuildValue("");

error:

   return NULL;
}

static char ssl_object_shutdown__doc__[] = 
"<method>\n"
"   <header>\n"
"      <memberof>Ssl</memberof>\n"
"      <name>shutdown</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method will issue a <constant>shutdown</constant> signal to it's peer. \n"
"         If this connection's peer has already initiated a shutdown this call\n"
"         will succeed, otherwise it will raise and exception.  In order to\n"
"         check the shutdown handshake was successful,\n"
"         <function>shutdown</function> must be called again.  If no\n"
"         exception is raised, the handshake is complete.  \n"
"      </para>\n"
"      <para>\n"
"         The odd\n"
"         implementation of this function reflects the underlying OpenSSL\n"
"         function, which reflects the SSL protocol.  Although rasing an\n"
"         exception is a bit annoying, the alternative, returning true all\n"
"         false will not tell you why the call failed and the exception\n"
"         will, at least that is the theory.  Look up the exact meaning\n"
"         of the exceptions in the OpenSSL man page SSL_get_error.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
ssl_object_shutdown(ssl_object *self, PyObject *args)
{
   int ret=0, err=0;

	if (!PyArg_ParseTuple(args, ""))
		goto error;
   
   ret = SSL_shutdown(self->ssl);

   if (ret <= 0) 
   {
      err = SSL_get_error( self->ssl, ret );
      PyErr_SetObject(SSLErrorObject, ssl_err_factory( err ) );
      goto error;
   }

   return Py_BuildValue("");

error:

   return NULL;
}

static char ssl_object_get_shutdown__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>Ssl</memberof>\n"
"      <name>getShutdown</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This function returns an integer indicating the state of the\n"
"         SSL connection. <constant>SSL_RECIEVED_SHUTDOWN</constant>\n"
"         will be set the if it's peer sends a <constant>shutdown</constant>\n"
"         signal or the underlying socket\n"
"         receives a close notify .  The possible values are:\n"
"      </para>\n"
"      <simplelist>\n"
"         <member><constant>SSL_NO_SHUTDOWN</constant></member>\n"
"         <member><constant>SSL_SENT_SHUTDOWN</constant></member>\n"
"         <member><constant>SSL_RECIEVED_SHUTDOWN</constant></member>\n"
"         <member><constant>SSL_SENT_SHUTDOWN</constant> | <constant>SSL_RECIEVED_SHUTDOWN</constant></member>\n"
"      </simplelist>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
ssl_object_get_shutdown(ssl_object *self, PyObject *args)
{
   int state=0;

	if (!PyArg_ParseTuple(args, ""))
		goto error;
   
   state = SSL_get_shutdown(self->ssl);

   return Py_BuildValue("i", state);

error:

   return NULL;
}

static char ssl_object_get_ciphers__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>Ssl</memberof>\n"
"      <name>getCiphers</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This function returns a list of available ciphers ordered from\n"
"         most favored to least.  This function must be called after\n"
"         <function>setFd</function>.  \n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
ssl_object_get_ciphers(ssl_object *self, PyObject *args)
{
   int inlist=0, i=0;
   const char *cipher=NULL;
   PyObject *list=NULL, *name=NULL;

	if (!PyArg_ParseTuple(args, ""))
		goto error;

   if (!self->ctxset)
      { PyErr_SetString( SSLErrorObject, "cannont be called before setFd()" ); goto error; }

   list = PyList_New(0);
   
   cipher = SSL_get_cipher_list(self->ssl, 0);
   while (cipher)
   {
      if ( !(name = PyString_FromString(cipher) ) )
         goto error;
      if ( PyList_Append( list, name ) != 0)
         goto error;
      cipher = SSL_get_cipher_list(self->ssl, ++i);
   }
   return Py_BuildValue("O", list);

error:

   if (list)
   {
      inlist = PyList_Size( list );
      for (i=0; i < inlist; i++)
      {
         name = PyList_GetItem( list, i );
         Py_DECREF(name);
      }
      Py_DECREF(list);
   }

   return NULL;
}

static char ssl_object_set_ciphers__doc__[] = 
"<method>\n"
"   <header>\n"
"      <memberof>Ssl</memberof>\n"
"      <name>setCiphers</name>\n"
"      <parameter>ciphers</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         <function>setCiphers</function>\n"
"         can help protect against certain types of attacks which try to\n"
"         coerce the server, client or both to negotiate a weak cipher.          \n"
"         <parameter>ciphers</parameter> should be a list of strings, as\n"
"         produced by <function>getCiphers</function> and described in the\n"
"         OpenSSL man page ciphers.   <function>setCiphers</function> should\n"
"         only be called after <function>setFd</function>.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
ssl_object_set_ciphers(ssl_object *self, PyObject *args)
{
   PyObject *ciphers=NULL;
   PyObject *cipher=NULL;
   int size=0, cipherstrlen=0, nextstrlen=0, i=0;
   char *cipherstr=NULL;

	if (!PyArg_ParseTuple(args, "O", &ciphers))
		goto error;

   if ( !(PyList_Check(ciphers) || PyTuple_Check(ciphers)) )
      { PyErr_SetString( PyExc_TypeError, "inapropriate type" ); goto error; }

   if (!self->ctxset)
      { PyErr_SetString( SSLErrorObject, "cannont be called before setFd()" ); goto error; }

   cipherstr = malloc(8);  //very bogus, realloc dosn't work with out some
                           //previously allocated memory! Really should.
   memset(cipherstr, 0, 8);
   size = PySequence_Size(ciphers);
   for (i=0; i < size; i++)
   {
      if ( !( cipher = PySequence_GetItem( ciphers, i ) ) )
         goto error;

      if ( !PyString_Check(cipher) )
         { PyErr_SetString( PyExc_TypeError, "inapropriate type" ); goto error; }

      cipherstrlen = strlen(cipherstr);
      nextstrlen = strlen( PyString_AsString(cipher) );

      if ( !(cipherstr = realloc( cipherstr, cipherstrlen + nextstrlen + 2)) )
         { PyErr_SetString( PyExc_TypeError, "could allocate memory" ); goto error; }

      if (cipherstrlen)
         strcat( cipherstr, ":\0" );

      strcat( cipherstr, PyString_AsString(cipher) );
      Py_DECREF(cipher);
      cipher = NULL;
   }
   SSL_set_cipher_list( self->ssl, cipherstr );
   free(cipherstr);
   return Py_BuildValue("");

error:

   if (cipherstr)
      free(cipherstr);

   Py_XDECREF(cipher);

   return NULL;
}

static char ssl_object_get_cipher__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>Ssl</memberof>\n"
"      <name>getCipher</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This function returns the current cipher in use.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
ssl_object_get_cipher(ssl_object *self, PyObject *args)
{
	if (!PyArg_ParseTuple(args, ""))
		goto error;

   if (!self->ctxset)
      { PyErr_SetString( SSLErrorObject, "cannont be called before setFd()" ); goto error; }
   
   return Py_BuildValue("s", SSL_get_cipher( self->ssl ));

error:

   return NULL;
}

static int stub_callback(int preverify_ok, X509_STORE_CTX *ctx)
{
   return 1;
}

static char ssl_object_set_verify_mode__doc__[] = 
"<method>\n"
"   <header>\n"
"      <memberof>Ssl</memberof>\n"
"      <name>setVerifyMode</name>\n"
"      <parameter>mode</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This function sets the behavior of the SSL handshake.  The\n"
"         parameter <parameter>mode</parameter> should be one of the\n"
"         following:\n"
"      </para>\n"
"      <simplelist>\n"
"         <member><constant>SSL_VERIFY_NONE</constant></member>\n"
"         <member><constant>SSL_VERIFY_PEER</constant></member>\n"
"      </simplelist>\n"
"      <para>\n"
"         See the OpenSSL man page <function>SSL_CTX_set_verify</function> \n"
"         for details.  This function must be called after <function>setfd</function> \n"
"         has been called.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
ssl_object_set_verify_mode(ssl_object *self, PyObject *args)
{
   int mode=0;

	if (!PyArg_ParseTuple(args, "i", &mode))
		goto error;

   if (self->ctxset)
      { PyErr_SetString( SSLErrorObject, "cannont be called after setfd()" ); goto error; }

   SSL_CTX_set_verify( self->ctx, mode, stub_callback );

   return Py_BuildValue("");

error:

   return NULL;
}

static struct PyMethodDef ssl_object_methods[] = {
	{"useCertificate",   (PyCFunction)ssl_object_use_certificate,  METH_VARARGS,	NULL},
	{"useKey",           (PyCFunction)ssl_object_use_key,	         METH_VARARGS,	NULL},
	{"checkKey",         (PyCFunction)ssl_object_check_key,	      METH_VARARGS,	NULL},
	{"setFd",	         (PyCFunction)ssl_object_set_fd,	         METH_VARARGS,	NULL},
	{"connect",	         (PyCFunction)ssl_object_connect,	         METH_VARARGS,	NULL},
	{"accept",	         (PyCFunction)ssl_object_accept,	         METH_VARARGS,	NULL},
	{"write",	         (PyCFunction)ssl_object_write,	         METH_VARARGS,	NULL},
	{"read",	            (PyCFunction)ssl_object_read,	            METH_VARARGS,	NULL},
	{"peerCertificate",  (PyCFunction)ssl_object_peer_certificate, METH_VARARGS,	NULL},
	{"clear",	         (PyCFunction)ssl_object_clear,	         METH_VARARGS,	NULL},
	{"shutdown",	      (PyCFunction)ssl_object_shutdown,	      METH_VARARGS,	NULL},
	{"getShutdown",	   (PyCFunction)ssl_object_get_shutdown,	   METH_VARARGS,	NULL},
	{"getCiphers",	      (PyCFunction)ssl_object_get_ciphers,	   METH_VARARGS,	NULL},
	{"setCiphers",	      (PyCFunction)ssl_object_set_ciphers,	   METH_VARARGS,	NULL},
	{"getCipher",	      (PyCFunction)ssl_object_get_cipher,	      METH_VARARGS,	NULL},
	{"setVerifyMode",	   (PyCFunction)ssl_object_set_verify_mode,  METH_VARARGS,	NULL},
 
	{NULL,		NULL}		/* sentinel */
};

static ssl_object *
newssl_object(int type)
{
	ssl_object *self;
   SSL_METHOD *method;

	
	if ( !(self = PyObject_NEW(ssl_object, &ssltype) ) )
		goto error;

   self->ctxset = 0;
   self->ssl = NULL;

   switch(type)
   {
      case SSLV2_SERVER_METHOD:  method = SSLv2_server_method();   break;
      case SSLV2_CLIENT_METHOD:  method = SSLv2_client_method();   break;
      case SSLV2_METHOD:         method = SSLv2_method();          break;
      case SSLV3_SERVER_METHOD:  method = SSLv3_server_method();   break;
      case SSLV3_CLIENT_METHOD:  method = SSLv3_client_method();   break;
      case SSLV3_METHOD:         method = SSLv3_method();          break;
      case TLSV1_SERVER_METHOD:  method = TLSv1_server_method();   break;
      case TLSV1_CLIENT_METHOD:  method = TLSv1_client_method();   break;
      case TLSV1_METHOD:         method = TLSv1_method();          break;
      case SSLV23_SERVER_METHOD: method = SSLv23_server_method();  break;
      case SSLV23_CLIENT_METHOD: method = SSLv23_client_method();  break;
      case SSLV23_METHOD:        method = SSLv23_method();         break;
                                                                     
      default:    
         { PyErr_SetString( SSLErrorObject, "unkown ctx method" ); goto error; }
                   
   } 

   if ( !(self->ctx = SSL_CTX_new( method ) ) )
      { PyErr_SetString( SSLErrorObject, "unable to create new ctx" ); goto error; }

	return self;

error:

   Py_XDECREF( self );
   return NULL;
}

static PyObject *
ssl_object_getattr(ssl_object *self, char *name)
{
	return Py_FindMethod(ssl_object_methods, (PyObject *)self, name);
}

static void
ssl_object_dealloc(ssl_object *self)
{
   SSL_free( self->ssl );
   SSL_CTX_free( self->ctx );
   PyObject_Del(self);
}

static char ssltype__doc__[] =
"<class>\n"
"   <header>\n"
"      <name>Ssl</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This class provides access to the Secure Socket Layer\n"
"         functionality of OpenSSL.  It is designed to be a simple as\n"
"         possible to use and is not designed for high performance\n"
"         applications which handle many simultaneous connections.  The\n"
"         original motivation for writing this library was to provide a\n"
"         security layer for network agents written in Python, for this\n"
"         application, good performance with multiple concurrent connections\n"
"         is not an issue. \n"
"      </para>\n"
"   </body>\n"
"</class>\n"
;

static PyTypeObject ssltype = {
	PyObject_HEAD_INIT(0)
	0,				                     /*ob_size*/
	"Ssl",			                  /*tp_name*/
	sizeof(ssl_object),               /*tp_basicsize*/
	0,				                     /*tp_itemsize*/
	(destructor)ssl_object_dealloc,	/*tp_dealloc*/
	(printfunc)0,		               /*tp_print*/
	(getattrfunc)ssl_object_getattr,	/*tp_getattr*/
	(setattrfunc)0,	               /*tp_setattr*/
	(cmpfunc)0,		                  /*tp_compare*/
	(reprfunc)0,	      	         /*tp_repr*/
	0,			                        /*tp_as_number*/
	0,		                           /*tp_as_sequence*/
	0,		                           /*tp_as_mapping*/
	(hashfunc)0,		               /*tp_hash*/
	(ternaryfunc)0,		            /*tp_call*/
	(reprfunc)0,		               /*tp_str*/
	0,
   0,
   0,
   0,
	ssltype__doc__                   /* Documentation string */
};
/*========== ssl Object ==========*/

/*========== asymmetric Object ==========*/
static asymmetric_object *
asymmetric_object_new(int cipher_type, int key_size)
{
   asymmetric_object *self=NULL;

   self = PyObject_New( asymmetric_object, &asymmetrictype );
   if (self == NULL)
      goto error;

   if (cipher_type != RSA_CIPHER)
      { PyErr_SetString( SSLErrorObject, "unsupported cipher" ); goto error; }

   if ( !(self->cipher = RSA_generate_key(key_size,RSA_F4,NULL,NULL) ) )
      {  PyErr_SetString( SSLErrorObject, "could not generate key" ); goto error; }

   self->key_type = RSA_PRIVATE_KEY;
   self->cipher_type = RSA_CIPHER;

   return self;

error:

   Py_XDECREF(self);
   return NULL;
}

static asymmetric_object *
asymmetric_object_pem_read(int key_type, BIO *in, char *pass)
{
   asymmetric_object *self=NULL;

   self = PyObject_New( asymmetric_object, &asymmetrictype );
   if (self == NULL)
      goto error;

   switch (key_type)
   {
      case RSA_PUBLIC_KEY:
      {
         if( !(self->cipher = PEM_read_bio_RSA_PUBKEY( in, NULL, NULL, NULL ) ) )
            {  PyErr_SetString( SSLErrorObject, "could not load public key" ); goto error; }
         self->key_type = RSA_PUBLIC_KEY;
         self->cipher_type = RSA_CIPHER;
         break;
      }
      case RSA_PRIVATE_KEY:
      {
         if( !(self->cipher = PEM_read_bio_RSAPrivateKey( in, NULL, NULL, pass) ) )
            {  PyErr_SetString( SSLErrorObject, "could not load private key" ); goto error; }
         self->key_type = RSA_PRIVATE_KEY;
         self->cipher_type = RSA_CIPHER;
         break;
      }
      default:
         {  PyErr_SetString( SSLErrorObject, "unkown key type" ); goto error; }
   }

   return self;

error:

   Py_XDECREF(self);
   return NULL;
}

static asymmetric_object *
asymmetric_object_der_read(int key_type, char *src, int len)
{
   asymmetric_object *self=NULL;
   unsigned char *ptr = src;

   self = PyObject_New( asymmetric_object, &asymmetrictype );
   if (self == NULL)
      goto error;

   switch (key_type)
   {
      case RSA_PUBLIC_KEY:
      {
         if( !(self->cipher = d2i_RSAPublicKey( NULL, &ptr, len ) ) )
            {  PyErr_SetString( SSLErrorObject, "could not load public key" ); goto error; }

         self->key_type = RSA_PUBLIC_KEY;
         self->cipher_type = RSA_CIPHER;
         break;
      }
      case RSA_PRIVATE_KEY:
      {
         if( !(self->cipher = d2i_RSAPrivateKey( NULL, &ptr, len ) ) )
            {  PyErr_SetString( SSLErrorObject, "could not load private key" ); goto error; }

         self->key_type = RSA_PRIVATE_KEY;
         self->cipher_type = RSA_CIPHER;
         break;
      }
      default:
         {  PyErr_SetString( SSLErrorObject, "unkown key type" ); goto error; }
   }

   return self;

error:

   Py_XDECREF(self);
   return NULL;
}

static char asymmetric_object_pem_write__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>Asymmetric</memberof>\n"
"      <name>pemWrite</name>\n"
"      <parameter>keytype</parameter>\n"
"      <parameter>ciphertype=None</parameter>\n"
"      <parameter>passphrase=None</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method is used to write <classname>Asymmetric</classname>\n"
"         objects out as strings.  The first argument should be either\n"
"         <constant>RSA_PUBLIC_KEY</constant> or\n"
"         <constant>RSA_PRIVATE_KEY</constant>.  Private keys are often\n"
"         saved in encrypted files to offer extra security above access\n"
"         control mechanisms.  If the <parameter>keytype</parameter> is\n"
"         <constant>RSA_PRIVATE_KEY</constant> a\n"
"         <parameter>ciphertype</parameter> and\n"
"         <parameter>passphrase</parameter> can also be specified.  The\n"
"         <parameter>ciphertype</parameter> should be one of those listed in\n"
"         the <classname>Symmetric</classname> class section.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
asymmetric_object_pem_write(asymmetric_object *self, PyObject *args)
{
   int key_type=0, cipher=0, len=0, ret=0;
   char *kstr=NULL, *buf=NULL;
   BIO *out_bio=NULL;
   PyObject *asymmetric=NULL;

	if (!PyArg_ParseTuple(args, "|iis", &key_type, &cipher, &kstr))
		goto error;

   if (key_type == 0)
      key_type = self->key_type;

   if ( !(out_bio = BIO_new(BIO_s_mem()) ) )
      { PyErr_SetString( SSLErrorObject, "unable to create new BIO" ); goto error; }

   if ( (kstr && !cipher) || (cipher && !kstr) )
      {PyErr_SetString(SSLErrorObject,"cipher type and key string must both be supplied");goto error;}


   switch( key_type )
   {
      case RSA_PRIVATE_KEY:
      {
         if (kstr && cipher)
         {
            if (!PEM_write_bio_RSAPrivateKey(out_bio, self->cipher, evp_cipher_factory(cipher), NULL, 0, NULL, kstr) )
               { PyErr_SetString( SSLErrorObject, "unable to write key" ); goto error; }
         }
         else
         {
            if (!PEM_write_bio_RSAPrivateKey(out_bio, self->cipher, NULL, NULL, 0, NULL, NULL) )
               { PyErr_SetString( SSLErrorObject, "unable to write key" ); goto error; }
         }
         break;
      }
      case RSA_PUBLIC_KEY:
      {
         if (kstr && cipher)
            { PyErr_SetString( SSLErrorObject, "public keys should not encrypted" ); goto error; }
         else
         {
            if (!PEM_write_bio_RSA_PUBKEY(out_bio, self->cipher) )
               { PyErr_SetString( SSLErrorObject, "unable to write key" ); goto error; }
         }
         break;
      }
      default:
         { PyErr_SetString( SSLErrorObject, "unsupported key type" ); goto error; }
   }

   if ( !(len = BIO_ctrl_pending(out_bio) ) )
      { PyErr_SetString( SSLErrorObject, "unable to get number of bytes in bio" ); goto error; }

   if ( !(buf = malloc(len) ) )
      { PyErr_SetString( SSLErrorObject, "unable to allocate memory" ); goto error; }

   if ( (ret = BIO_read( out_bio, buf, len ) ) != len )
      { PyErr_SetString( SSLErrorObject, "unable to write out key" ); goto error; }

   asymmetric = Py_BuildValue("s#", buf, len);

   BIO_free(out_bio);
   free(buf);
   return asymmetric;

error:

   if (out_bio);
      BIO_free(out_bio);

   if (buf)
      free(buf);

   return NULL;
}

static char asymmetric_object_der_write__doc__[] = 
"<method>"
"   <header>"
"      <memberof>Asymmetric</memberof>"
"      <name>derWrite</name>"
"      <parameter>keytype</parameter>"
"   </header>"
"   <body>"
"      <para>"
"         This method is used to write <classname>Asymmetric</classname>"
"         objects out as strings.  The first argument should be either"
"         <constant>RSA_PUBLIC_KEY</constant> or "
"         <constant>RSA_PRIVATE_KEY</constant>."
"      </para>"
"   </body>"
"</method>"
;

static PyObject *
asymmetric_object_der_write(asymmetric_object *self, PyObject *args)
{
   int len=0, key_type=0;
   unsigned char *buf=NULL, *p=NULL;
   PyObject *asymmetric=NULL;

	if (!PyArg_ParseTuple(args, "|i", &key_type))
		goto error;

   if (key_type == 0)
      key_type = self->key_type;

   switch( key_type )
   {
      case RSA_PRIVATE_KEY:
      {
         len = i2d_RSAPrivateKey(self->cipher, NULL);
         if ( !(buf = malloc(len) ) )
            { PyErr_SetString( SSLErrorObject, "could not allocate memory" ); goto error; }
         p = buf;
         if (!i2d_RSAPrivateKey(self->cipher, &buf) )
            { PyErr_SetString( SSLErrorObject, "unable to write key" ); goto error; }
         break;
      }
      case RSA_PUBLIC_KEY:
      {
         len = i2d_RSAPublicKey(self->cipher, NULL);
         if ( !(buf = malloc(len) ) )
            { PyErr_SetString( SSLErrorObject, "could not allocate memory" ); goto error; }
         p = buf;
         if (!i2d_RSAPublicKey(self->cipher, &buf) )
            { PyErr_SetString( SSLErrorObject, "unable to write key" ); goto error; }
         break;
      }
      default:
         { PyErr_SetString( SSLErrorObject, "unsupported key type" ); goto error; }
   }

   asymmetric = Py_BuildValue("s#", p, len);

   free(p);
   return asymmetric;

error:

   if (p)
      free(p);

   return NULL;
}

static char asymmetric_object_public_encrypt__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>Asymmetric</memberof>\n"
"      <name>publicEncrypt</name>\n"
"      <parameter>plaintext</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method is used to encrypt the <parameter>plaintext</parameter>\n"
"         using a public key. It should be noted; in practice this\n"
"         function would be used almost exclusively to encrypt symmetric cipher\n"
"         keys and not data since asymmetric cipher operations are very slow.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
asymmetric_object_public_encrypt(asymmetric_object *self, PyObject *args)
{
   char *plain_text=NULL, *cipher_text=NULL;
   int len=0, size=0;
   PyObject *obj=NULL;

   switch( self->cipher_type )
   {
      case RSA_CIPHER:
      {
         if (!PyArg_ParseTuple(args, "s#", &plain_text, &len))
            goto error;

         size = RSA_size(self->cipher);
         if ( len > size )
            { PyErr_SetString( SSLErrorObject, "plain text is too long" ); goto error; }

         if ( !(cipher_text = malloc( size + 16 ) ) )
            { PyErr_SetString( SSLErrorObject, "could not allocate memory" ); goto error; }

         if ( (len = RSA_public_encrypt( len, plain_text, cipher_text, self->cipher, RSA_PKCS1_PADDING ) ) < 0 )
            { PyErr_SetString( SSLErrorObject, "could not encrypt plain text" ); goto error; }
         break;
      }
      default:
         { PyErr_SetString( SSLErrorObject, "unsupported cipher type" ); goto error; }
   }

   obj = Py_BuildValue("s#", cipher_text, len);
   free( cipher_text );
   return obj;

error:

   if (cipher_text)
      free(cipher_text);

   return NULL;
}

static char asymmetric_object_private_encrypt__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>Asymmetric</memberof>\n"
"      <name>privateEncrypt</name>\n"
"      <parameter>plaintext</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method is used to encrypt the <parameter>plaintext</parameter>\n"
"         using a private key. It should be noted; in practice this\n"
"         function would be used almost exclusively to encrypt symmetric cipher\n"
"         keys and not data since asymmetric cipher operations are very slow.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
asymmetric_object_private_encrypt(asymmetric_object *self, PyObject *args)
{
   char *plain_text=NULL, *cipher_text=NULL;
   int len=0, size=0;
   PyObject *obj=NULL;

   if ( !(self->key_type == RSA_PRIVATE_KEY) ) 
      { PyErr_SetString( SSLErrorObject, "cannot perform private encryption with this key" ); goto error; }

   if (!PyArg_ParseTuple(args, "s#", &plain_text, &len) )
      goto error;

   size = RSA_size(self->cipher);
   if ( len > size )
      { PyErr_SetString( SSLErrorObject, "plain text is too long" ); goto error; }

   if ( !(cipher_text = malloc( size + 16 ) ) )
      { PyErr_SetString( SSLErrorObject, "could not allocate memory" ); goto error; }

   if ( (len = RSA_private_encrypt( len, plain_text, cipher_text, self->cipher, RSA_PKCS1_PADDING ) ) < 0 )
      { PyErr_SetString( SSLErrorObject, "could not encrypt plain text" ); goto error; }

   obj = Py_BuildValue("s#", cipher_text, len);
   free( cipher_text );
   return obj;

error:

   if (cipher_text)
      free(cipher_text);

   return NULL;
}

static char asymmetric_object_public_decrypt__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>Asymmetric</memberof>\n"
"      <name>publicDecrypt</name>\n"
"      <parameter>ciphertext</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method is used to decrypt the\n"
"         <parameter>ciphertext</parameter> which has been encrypted\n"
"         using the corresponding private key and the\n"
"         <function>privateEncrypt</function> function.  \n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
asymmetric_object_public_decrypt(asymmetric_object *self, PyObject *args)
{
   char *plain_text=NULL, *cipher_text=NULL;
   int len=0, size=0;
   PyObject *obj=NULL;

   switch( self->cipher_type )
   {
      case RSA_CIPHER:
      {
         if (!PyArg_ParseTuple(args, "s#", &cipher_text, &len))
            goto error;
   
         size = RSA_size(self->cipher);
         if ( len > size )
            { PyErr_SetString( SSLErrorObject, "cipher text is too long" ); goto error; }

         if ( !(plain_text = malloc( size + 16 ) ) )
            { PyErr_SetString( SSLErrorObject, "could not allocate memory" ); goto error; }

         if ( (len = RSA_public_decrypt( len, cipher_text, plain_text, self->cipher, RSA_PKCS1_PADDING ) ) < 0 )
            { PyErr_SetString( SSLErrorObject, "could not decrypt cipher text" ); goto error; }
         break;
      }
      default:
         { PyErr_SetString( SSLErrorObject, "unsupported cipher type" ); goto error; }
   }

   obj = Py_BuildValue("s#", plain_text, len);
   free( plain_text );
   return obj;

error:

   if (plain_text)
      free(plain_text);

   return NULL;
}

static char asymmetric_object_private_decrypt__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>Asymmetric</memberof>\n"
"      <name>privateDecrypt</name>\n"
"      <parameter>ciphertext</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method is used to decrypt ciphertext which has been encrypted\n"
"         using the corresponding public key and the\n"
"         <function>publicEncrypt</function> function.  \n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
asymmetric_object_private_decrypt(asymmetric_object *self, PyObject *args)
{
   char *plain_text=NULL, *cipher_text=NULL;
   int len=0, size=0;
   PyObject *obj=NULL;

   if ( !(self->key_type == RSA_PRIVATE_KEY) ) 
      { PyErr_SetString( SSLErrorObject, "cannot perform private decryption with this key" ); goto error; }

   if (!PyArg_ParseTuple(args, "s#", &cipher_text, &len))
      goto error;

   size = RSA_size(self->cipher);
   if ( len > size )
      { PyErr_SetString( SSLErrorObject, "cipher text is too long" ); goto error; }

   if ( !(plain_text = malloc( size + 16 ) ) )
      { PyErr_SetString( SSLErrorObject, "could not allocate memory" ); goto error; }

   if ( (len = RSA_private_decrypt( len, cipher_text, plain_text, self->cipher, RSA_PKCS1_PADDING ) ) < 0 )
      { PyErr_SetString( SSLErrorObject, "could not decrypt cipher text" ); goto error; }

   obj = Py_BuildValue("s#", plain_text, len);
   free( plain_text );
   return obj;

error:

   if (plain_text)
      free(plain_text);
   return NULL;
}

static char asymmetric_object_sign__doc__[] = 
"<method>\n"
"   <header>\n"
"      <memberof>Asymmetric</memberof>\n"
"      <name>sign</name>\n"
"      <parameter>digesttext</parameter>\n"
"      <parameter>digesttype</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method is used to produce a signed digest text.  \n"
"         This instance of\n"
"         <classname>Asymmetric</classname> should be a private key used for\n"
"         signing.  The parameter\n"
"         <parameter>digesttext</parameter> should be a digest of the \n"
"         data to protect against alteration and\n"
"         finally <parameter>digesttype</parameter> should be one of the\n"
"         following:\n"
"      </para>\n"
"      <simplelist>\n"
"         <member><constant>MD2_DIGEST</constant></member>\n"
"         <member><constant>MD5_DIGEST</constant></member>\n"
"         <member><constant>SHA_DIGEST</constant></member>\n"
"         <member><constant>SHA1_DIGEST</constant></member>\n"
"         <member><constant>RIPEMD160_DIGEST</constant></member>\n"
"      </simplelist>\n"
"      <para>\n"
"         If the procedure was successful, a string containing the signed\n"
"         digest is returned. \n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
asymmetric_object_sign(asymmetric_object *self, PyObject *args)
{
   char *digest_text=NULL, *signed_text=NULL; 
   int digest_len=0, digest_type=0, digest_nid=0, signed_len=0;
   PyObject *obj=NULL;

	if (!PyArg_ParseTuple(args, "s#i", &digest_text, &digest_len, &digest_type))
		goto error;

   if (self->key_type != RSA_PRIVATE_KEY)
      { PyErr_SetString( SSLErrorObject, "unsupported key type" ); goto error; }
    
   if ( !(signed_text = malloc( RSA_size(self->cipher) ) ) )
      { PyErr_SetString( SSLErrorObject, "could not allocate memory" ); goto error; }

   switch(digest_type)
   {
      case MD2_DIGEST:
         { digest_nid = NID_md2; digest_len = MD2_DIGEST_LENGTH; break; }
      case MD5_DIGEST:
         { digest_nid = NID_md5; digest_len = MD5_DIGEST_LENGTH; break; }
      case SHA_DIGEST:
         { digest_nid = NID_sha; digest_len = SHA_DIGEST_LENGTH; break; }
      case SHA1_DIGEST:
         { digest_nid = NID_sha1; digest_len = SHA_DIGEST_LENGTH; break; }
      case RIPEMD160_DIGEST:
         { digest_nid = NID_ripemd160; digest_len = RIPEMD160_DIGEST_LENGTH; break; }
      default:
         { PyErr_SetString( SSLErrorObject, "unsupported digest" ); goto error; }
   }
   if ( !(RSA_sign( digest_nid, digest_text, digest_len, signed_text, &signed_len, self->cipher ) ) )
      { PyErr_SetString( SSLErrorObject, "could not sign digest" ); goto error; }

   obj = Py_BuildValue("s#", signed_text, signed_len);
   free(signed_text);
   return obj;

error:

   if (signed_text)
      free(signed_text);

   return NULL;
}

static char asymmetric_object_verify__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>Asymmetric</memberof>\n"
"      <name>verify</name>\n"
"      <parameter>signedtext</parameter>\n"
"      <parameter>digesttext</parameter>\n"
"      <parameter>digesttype</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method is used to verify a signed digest text.  \n"
"      </para>\n"
"       <example>\n"
"         <title><function>verify</function> method usage</title>\n"
"         <programlisting>\n"
"      plain_text = 'Hello World!'\n"
"      print '\tPlain text:', plain_text\n"
"      digest = POW.Digest( POW.RIPEMD160_DIGEST )\n"
"      digest.update( plain_text )\n"
"      print '\tDigest text:', digest.digest()\n"
"\n"
"      privateFile = open('test/private.key', 'r')\n"
"      privateKey = POW.pemRead( POW.RSA_PRIVATE_KEY, privateFile.read(), 'pass' )\n"
"      privateFile.close()\n"
"      signed_text =  privateKey.sign(digest.digest(), POW.RIPEMD160_DIGEST)\n"
"      print '\tSigned text:', signed_text\n"
"\n"
"      digest2 = POW.Digest( POW.RIPEMD160_DIGEST )\n"
"      digest2.update( plain_text )\n"
"      publicFile = open('test/public.key', 'r')\n"
"      publicKey = POW.pemRead( POW.RSA_PUBLIC_KEY, publicFile.read() )\n"
"      publicFile.close()\n"
"      if publicKey.verify( signed_text, digest2.digest(), POW.RIPEMD160_DIGEST ):\n"
"         print 'Signing verified!'\n"
"      else:\n"
"         print 'Signing gone wrong!'\n"
"         </programlisting>\n"
"      </example>\n"
"      <para>\n"
"         The parameter <parameter>signedtext</parameter> should be a \n"
"         signed digest text.  This instance of\n"
"         <classname>Asymmetric</classname> should correspond to the private\n"
"         key used to sign the digest.  The parameter\n"
"         <parameter>digesttext</parameter> should be a digest of the same\n"
"         data used to produce the <parameter>signedtext</parameter> and\n"
"         finally <parameter>digesttype</parameter> should be one of the\n"
"         following:\n"
"      </para>\n"
"      <simplelist>\n"
"         <member><constant>MD2_DIGEST</constant></member>\n"
"         <member><constant>MD5_DIGEST</constant></member>\n"
"         <member><constant>SHA_DIGEST</constant></member>\n"
"         <member><constant>SHA1_DIGEST</constant></member>\n"
"         <member><constant>RIPEMD160_DIGEST</constant></member>\n"
"      </simplelist>\n"
"      <para>\n"
"         If the procedure was successful, 1 is returned, otherwise 0 is\n"
"         returned.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;
static PyObject *
asymmetric_object_verify(asymmetric_object *self, PyObject *args)
{
   char *digest_text=NULL, *signed_text=NULL; 
   int digest_len=0, digest_type=0, digest_nid=0, signed_len=0, result=0;

	if (!PyArg_ParseTuple(args, "s#s#i", &signed_text, &signed_len, &digest_text, &digest_len, &digest_type))
		goto error;

   switch(digest_type)
   {
      case MD2_DIGEST:
         { digest_len = MD2_DIGEST_LENGTH; digest_nid = NID_md2; break; }
      case MD5_DIGEST:
         { digest_len = MD5_DIGEST_LENGTH; digest_nid = NID_md5; break; }
      case SHA_DIGEST:
         { digest_len = SHA_DIGEST_LENGTH; digest_nid = NID_sha; break; }
      case SHA1_DIGEST:
         { digest_len = SHA_DIGEST_LENGTH; digest_nid = NID_sha1; break; }
      case RIPEMD160_DIGEST:
         { digest_len = RIPEMD160_DIGEST_LENGTH; digest_nid = NID_ripemd160; break; }
      default:
         { PyErr_SetString( SSLErrorObject, "unsupported digest" ); goto error; }
   }
   result = RSA_verify( digest_nid, digest_text, digest_len, signed_text, signed_len, self->cipher );

   return Py_BuildValue("i", result);

error:

   return NULL;
}

static struct PyMethodDef asymmetric_object_methods[] = {
   {"pemWrite",      (PyCFunction)asymmetric_object_pem_write,       METH_VARARGS,  NULL}, 
   {"derWrite",      (PyCFunction)asymmetric_object_der_write,       METH_VARARGS,  NULL}, 
   {"publicEncrypt", (PyCFunction)asymmetric_object_public_encrypt,  METH_VARARGS,  NULL}, 
   {"privateEncrypt",(PyCFunction)asymmetric_object_private_encrypt, METH_VARARGS,  NULL}, 
   {"privateDecrypt",(PyCFunction)asymmetric_object_private_decrypt, METH_VARARGS,  NULL}, 
   {"publicDecrypt", (PyCFunction)asymmetric_object_public_decrypt,  METH_VARARGS,  NULL}, 
   {"sign",          (PyCFunction)asymmetric_object_sign,            METH_VARARGS,  NULL}, 
   {"verify",        (PyCFunction)asymmetric_object_verify,          METH_VARARGS,  NULL}, 
 
	{NULL,		NULL}		/* sentinel */
};

static PyObject *
asymmetric_object_getattr(asymmetric_object *self, char *name)
{
	return Py_FindMethod(asymmetric_object_methods, (PyObject *)self, name);
}

static void
asymmetric_object_dealloc(asymmetric_object *self, char *name)
{
   switch( self->cipher_type )
   {
      case RSA_CIPHER: 
      {
         RSA_free( self->cipher ); 
         break;
      }
   }
   PyObject_Del(self);
}

static char asymmetrictype__doc__[] =
"<class>\n"
"   <header>\n"
"      <name>Asymmetric</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This class provides access to RSA asymmetric ciphers in OpenSSL.\n"
"         Other ciphers will probably be supported in the future but this is\n"
"         not a priority.\n"
"      </para>\n"
"   </body>\n"
"</class>\n"
;

static PyTypeObject asymmetrictype = {
	PyObject_HEAD_INIT(0)
	0,				                           /*ob_size*/
	"Asymmetric",			                  /*tp_name*/
	sizeof(asymmetric_object),		         /*tp_basicsize*/
	0,				                           /*tp_itemsize*/
	(destructor)asymmetric_object_dealloc,	/*tp_dealloc*/
	(printfunc)0,		                     /*tp_print*/
	(getattrfunc)asymmetric_object_getattr,	/*tp_getattr*/
	(setattrfunc)0,	                     /*tp_setattr*/
	(cmpfunc)0,		                        /*tp_compare*/
	(reprfunc)0,      		               /*tp_repr*/
	0,			                              /*tp_as_number*/
	0,		                                 /*tp_as_sequence*/
	0,		                                 /*tp_as_mapping*/
	(hashfunc)0,		                     /*tp_hash*/
	(ternaryfunc)0,		                  /*tp_call*/
	(reprfunc)0,		                     /*tp_str*/
	0,
   0,
   0,
   0,
	asymmetrictype__doc__                   /* Documentation string */
};
/*========== asymmetric Code ==========*/

/*========== symmetric Code ==========*/
static symmetric_object *
symmetric_object_new(int cipher_type)
{
   symmetric_object *self=NULL;

   self = PyObject_New( symmetric_object, &symmetrictype );
   if (self == NULL)
      goto error;

   self->cipher_type = cipher_type;
   EVP_CIPHER_CTX_init( &self->cipher_ctx );

   return self;

error:

   Py_XDECREF(self);
   return NULL;
}

static char symmetric_object_encrypt_init__doc__[] = 
"<method>\n"
"   <header>\n"
"      <memberof>Symmetric</memberof>\n"
"      <name>encryptInit</name>\n"
"      <parameter>key</parameter>\n"
"      <parameter>initialvalue=''</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method sets up the cipher object to start encrypting a stream\n"
"         of data.  The first parameter is the key used to encrypt the\n"
"         data.  The second, the <parameter>initialvalue</parameter> serves\n"
"         a similar purpose the the salt supplied to the Unix\n"
"         <function>crypt</function> function.\n"
"         The <parameter>initialvalue</parameter> is normally chosen at random and \n"
"         often transmitted with the encrypted data, its purpose is to prevent \n"
"         two identical plain texts resulting in two identical cipher texts.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
symmetric_object_encrypt_init(symmetric_object *self, PyObject *args)
{
   char *key=NULL, *iv=NULL, nulliv [] = "";
   EVP_CIPHER *cipher=NULL;

	if (!PyArg_ParseTuple(args, "s|s", &key, &iv))
		goto error;

   if (!iv)
      iv = nulliv;

   if ( !(cipher = evp_cipher_factory( self->cipher_type ) ) )
         { PyErr_SetString( SSLErrorObject, "unsupported cipher" ); goto error; }

   if ( !EVP_EncryptInit( &self->cipher_ctx, cipher, key, iv ) )
      { PyErr_SetString( SSLErrorObject, "could not initialise cipher" ); goto error; }
   
   return Py_BuildValue("");

error:

   return NULL;
}

static char symmetric_object_decrypt_init__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>Symmetric</memberof>\n"
"      <name>decryptInit</name>\n"
"      <parameter>key</parameter>\n"
"      <parameter>initialvalue=''</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method sets up the cipher object to start decrypting a stream\n"
"         of data.  The first value must be the key used to encrypt the\n"
"         data.  The second parameter is the <parameter>initialvalue</parameter> \n"
"         used to encrypt the data.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
symmetric_object_decrypt_init(symmetric_object *self, PyObject *args)
{
   char *key=NULL, *iv=NULL, nulliv [] = "";
   EVP_CIPHER *cipher=NULL;

	if (!PyArg_ParseTuple(args, "s|s", &key, &iv))
		goto error;

   if (!iv)
      iv = nulliv;

   if ( !(cipher = evp_cipher_factory( self->cipher_type ) ) )
         { PyErr_SetString( SSLErrorObject, "unsupported cipher" ); goto error; }

   if ( !EVP_DecryptInit( &self->cipher_ctx, cipher, key, iv ) )
      { PyErr_SetString( SSLErrorObject, "could not initialise cipher" ); goto error; }
   
   return Py_BuildValue("");

error:

   return NULL;
}

static char symmetric_object_update__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>Symmetric</memberof>\n"
"      <name>update</name>\n"
"      <parameter>data</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method is used to process the bulk of data being encrypted\n"
"         or decrypted by the cipher object.  <parameter>data</parameter>\n"
"         should be a string.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
symmetric_object_update(symmetric_object *self, PyObject *args)
{
   int inl=0, outl=0;
   char *in=NULL, *out=NULL;
   PyObject *py_out=NULL;

	if (!PyArg_ParseTuple(args, "s#", &in, &inl))
		goto error;

   if ( !(out = malloc( inl + EVP_CIPHER_CTX_block_size( &self->cipher_ctx) ) ) )
      { PyErr_SetString( SSLErrorObject, "could not allocate memory" ); goto error; }

   if ( !EVP_CipherUpdate( &self->cipher_ctx, out, &outl, in, inl ) )
      { PyErr_SetString( SSLErrorObject, "could not update cipher" ); goto error; }

   if ( !(py_out = Py_BuildValue("s#", out, outl) ) )
      { PyErr_SetString( SSLErrorObject, "could not allocate memory" ); goto error; }

   free(out);
   return py_out;

error:

   if (out)
      free(out);

   return NULL;
}

static char symmetric_object_final__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>Symmetric</memberof>\n"
"      <name>final</name>\n"
"      <parameter>size=1024</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         Most ciphers are block ciphers, that is they encrypt or decrypt a block of\n"
"         data at a time.  Often the data being processed will not fill an\n"
"         entire block, this method processes these half-empty blocks.  A\n"
"         string is returned of a maximum length <parameter>size</parameter>. \n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
symmetric_object_final(symmetric_object *self, PyObject *args)
{
   int outl=0, size=1024;
   char *out=NULL;
   PyObject *py_out=NULL;

	if (!PyArg_ParseTuple(args, "|i", &size))
		goto error;

   if ( !(out = malloc( size + EVP_CIPHER_CTX_block_size( &self->cipher_ctx) ) ) )
      { PyErr_SetString( SSLErrorObject, "could not allocate memory" ); goto error; }

   if ( !EVP_CipherFinal( &self->cipher_ctx, out, &outl ) )
      { PyErr_SetString( SSLErrorObject, "could not update cipher" ); goto error; }

   if ( !(py_out = Py_BuildValue("s#", out, outl) ) )
      { PyErr_SetString( SSLErrorObject, "could not allocate memory" ); goto error; }

   free(out);
   return py_out;

error:

   if (out)
      free(out);

   return NULL;
}

static struct PyMethodDef symmetric_object_methods[] = {
   {"encryptInit",   (PyCFunction)symmetric_object_encrypt_init,  METH_VARARGS,  NULL}, 
   {"decryptInit",   (PyCFunction)symmetric_object_decrypt_init,  METH_VARARGS,  NULL}, 
   {"update",        (PyCFunction)symmetric_object_update,        METH_VARARGS,  NULL}, 
   {"final",         (PyCFunction)symmetric_object_final,         METH_VARARGS,  NULL}, 
 
	{NULL,		NULL}		/* sentinel */
};

static PyObject *
symmetric_object_getattr(symmetric_object *self, char *name)
{
	return Py_FindMethod(symmetric_object_methods, (PyObject *)self, name);
}

static void
symmetric_object_dealloc(symmetric_object *self, char *name)
{
   PyObject_Del(self);
}

static char symmetrictype__doc__[] =
"<class>\n"
"   <header>\n"
"      <name>Symmetric</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This class provides access to all the symmetric ciphers in OpenSSL.\n"
"         Initialisation of the cipher structures is performed late, only\n"
"         when <function>encryptInit</function> or\n"
"         <function>decryptInit</function> is called, the\n"
"         constructor only records the cipher type.  It is possible to reuse\n"
"         the <classname>Symmetric</classname> objects by calling\n"
"         <function>encryptInit</function> or <function>decryptInit</function>\n"
"         again.\n"
"      </para>\n"
"      <example>\n"
"         <title><classname>Symmetric</classname> class usage</title>\n"
"         <programlisting>\n"
"      passphrase = 'my silly passphrase'\n"
"      md5 = POW.Digest( POW.MD5_DIGEST )\n"
"      md5.update( passphrase )\n"
"      password = md5.digest()[:8]\n"
"\n"
"      plaintext = 'cast test message'\n"
"      cast = POW.Symmetric( POW.CAST5_CFB ) \n"
"      cast.encryptInit( password )\n"
"      ciphertext = cast.update(plaintext) + cast.final()\n"
"      print 'Cipher text:', ciphertext\n"
"\n"
"      cast.decryptInit( password )\n"
"      out = cast.update( ciphertext ) + cast.final()\n"
"      print 'Deciphered text:', out\n"
"         </programlisting>\n"
"      </example>\n"
"   </body>\n"
"</class>\n"
;

static PyTypeObject symmetrictype = {
	PyObject_HEAD_INIT(0)
	0,				                           /*ob_size*/
	"Symmetric",			                     /*tp_name*/
	sizeof(symmetric_object),		         /*tp_basicsize*/
	0,				                           /*tp_itemsize*/
	(destructor)symmetric_object_dealloc,	/*tp_dealloc*/
	(printfunc)0,		                     /*tp_print*/
	(getattrfunc)symmetric_object_getattr,	/*tp_getattr*/
	(setattrfunc)0,	                     /*tp_setattr*/
	(cmpfunc)0,		                        /*tp_compare*/
	(reprfunc)0,      		               /*tp_repr*/
	0,			                              /*tp_as_number*/
	0,		                                 /*tp_as_sequence*/
	0,		                                 /*tp_as_mapping*/
	(hashfunc)0,		                     /*tp_hash*/
	(ternaryfunc)0,		                  /*tp_call*/
	(reprfunc)0,		                     /*tp_str*/
	0,
   0,
   0,
   0,
	symmetrictype__doc__                    /* Documentation string */
};
/*========== symmetric Code ==========*/

/*========== digest Code ==========*/
static digest_object *
digest_object_new(int digest_type)
{
   digest_object *self=NULL;

   self = PyObject_New( digest_object, &digesttype );
   if (self == NULL)
      goto error;

   switch(digest_type)
   {
      case MD2_DIGEST: 
         { self->digest_type = MD2_DIGEST; EVP_DigestInit( &self->digest_ctx, EVP_md2() ); break; }
      case MD5_DIGEST: 
         { self->digest_type = MD5_DIGEST; EVP_DigestInit( &self->digest_ctx, EVP_md5() ); break; }
      case SHA_DIGEST: 
         { self->digest_type = SHA_DIGEST; EVP_DigestInit( &self->digest_ctx, EVP_sha() ); break; }
      case SHA1_DIGEST: 
         { self->digest_type = SHA1_DIGEST; EVP_DigestInit( &self->digest_ctx, EVP_sha1() ); break; }
      case RIPEMD160_DIGEST: 
         { self->digest_type = RIPEMD160_DIGEST; EVP_DigestInit( &self->digest_ctx, EVP_ripemd160() ); break; }
      default:
         { PyErr_SetString( SSLErrorObject, "unsupported digest" ); goto error; }
   }

   return self;

error:

   Py_XDECREF(self);
   return NULL;
}

static char digest_object_update__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>Digest</memberof>\n"
"      <name>update</name>\n"
"      <parameter>data</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method updates the internal structures of the \n"
"         <classname>Digest</classname> object with <parameter>data</parameter>.\n"
"         <parameter>data</parameter> should be a string.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
digest_object_update(digest_object *self, PyObject *args)
{
   char *data=NULL;
   int len=0;

	if (!PyArg_ParseTuple(args, "s#", &data, &len))
		goto error;

   EVP_DigestUpdate( &self->digest_ctx, data, len );

   return Py_BuildValue("");

error:

   return NULL;
}

static char digest_object_copy__doc__[] = 
"<method>\n"
"   <header>\n"
"      <memberof>Digest</memberof>\n"
"      <name>copy</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method returns a copy of the <classname>Digest</classname>\n"
"         object.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
digest_object_copy(digest_object *self, PyObject *args)
{
   digest_object *new=NULL;

   if ( !(new = PyObject_New( digest_object, &digesttype ) ) )
      { PyErr_SetString( SSLErrorObject, "could not allocate memory" ); goto error; }

   new->digest_type = self->digest_type;
   memcpy( &new->digest_ctx, &self->digest_ctx, sizeof(EVP_MD_CTX) );

   return (PyObject*)new;

error:

   Py_XDECREF(new);
   return NULL;
}

static char digest_object_digest__doc__[] = 
"<method>\n"
"   <header>\n"
"      <memberof>Digest</memberof>\n"
"      <name>digest</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method returns the digest of all the data which has been\n"
"         processed.  This function can be called at any time and will not\n"
"         effect the internal structure of the <classname>digest</classname>\n"
"         object.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
digest_object_digest(digest_object *self, PyObject *args)
{
   char digest_text[EVP_MAX_MD_SIZE];
   void *md_copy=NULL;
   int digest_len=0;

	if (!PyArg_ParseTuple(args, ""))
		goto error;

   if ( !(md_copy = malloc( sizeof(EVP_MD_CTX) ) ) )
      { PyErr_SetString( SSLErrorObject, "could not allocate memory" ); goto error; }
   memcpy( md_copy, &self->digest_ctx, sizeof(EVP_MD_CTX) );
   EVP_DigestFinal( md_copy, digest_text, &digest_len );

   free(md_copy);
   return Py_BuildValue("s#", digest_text, digest_len);

error:

   if (md_copy)
      free(md_copy);

   return NULL;
}

static struct PyMethodDef digest_object_methods[] = {
   {"update",           (PyCFunction)digest_object_update,  METH_VARARGS, NULL}, 
   {"digest",           (PyCFunction)digest_object_digest,  METH_VARARGS, NULL}, 
   {"copy",             (PyCFunction)digest_object_copy,    METH_VARARGS, NULL}, 
 
	{NULL,		NULL}		/* sentinel */
};

static PyObject *
digest_object_getattr(digest_object *self, char *name)
{
	return Py_FindMethod(digest_object_methods, (PyObject *)self, name);
}

static void
digest_object_dealloc(digest_object *self, char *name)
{
   PyObject_Del(self);
}

static char digesttype__doc__[] = 
"<class>\n"
"   <header>\n"
"      <name>Digest</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This class provides access to the digest functionality of OpenSSL.\n"
"         It emulates the digest modules in the Python Standard Library but\n"
"         does not currently support the <function>hexdigest</function>\n"
"         function.\n"
"      </para>\n"
"      <example>\n"
"         <title><classname>digest</classname> class usage</title>\n"
"         <programlisting>\n"
"      plain_text = 'Hello World!'\n"
"      sha1 = POW.Digest( POW.SHA1_DIGEST )\n"
"      sha1.update( plain_text )\n"
"      print '\tPlain text: Hello World! =>', sha1.digest()\n"
"         </programlisting>\n"
"      </example>\n"
"   </body>\n"
"</class>\n"
;

static PyTypeObject digesttype = {
	PyObject_HEAD_INIT(0)
	0,				                        /*ob_size*/
	"Digest",		                     /*tp_name*/
	sizeof(digest_object),		         /*tp_basicsize*/
	0,				                        /*tp_itemsize*/
	(destructor)digest_object_dealloc,	/*tp_dealloc*/
	(printfunc)0,		                  /*tp_print*/
	(getattrfunc)digest_object_getattr,	/*tp_getattr*/
	(setattrfunc)0,	                  /*tp_setattr*/
	(cmpfunc)0,		                     /*tp_compare*/
	(reprfunc)0,      		            /*tp_repr*/
	0,			                           /*tp_as_number*/
	0,		                              /*tp_as_sequence*/
	0,		                              /*tp_as_mapping*/
	(hashfunc)0,		                  /*tp_hash*/
	(ternaryfunc)0,		               /*tp_call*/
	(reprfunc)0,		                  /*tp_str*/
	0,
   0,
   0,
   0,
	digesttype__doc__                   /* Documentation string */
};
/*========== digest Code ==========*/

/*========== hmac Code ==========*/
static hmac_object *
hmac_object_new(int digest_type, char *key, int key_len)
{
   hmac_object *self=NULL;
   EVP_MD *md=NULL;

   self = PyObject_New( hmac_object, &hmactype );
   if (self == NULL)
      goto error;

   switch(digest_type)
   {
      case MD2_DIGEST: 
         { md = EVP_md2(); break; }
      case MD5_DIGEST: 
         { md = EVP_md5(); break; }
      case SHA_DIGEST: 
         { md = EVP_sha(); break; }
      case SHA1_DIGEST: 
         { md = EVP_sha1(); break; }
      case RIPEMD160_DIGEST: 
         { md = EVP_ripemd160(); break; }
      default:
         { PyErr_SetString( SSLErrorObject, "unsupported digest" ); goto error; }
   }

   HMAC_Init( &self->hmac_ctx, key, key_len, md );

   return self;

error:

   Py_XDECREF(self);
   return NULL;
}

static char hmac_object_update__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>Hmac</memberof>\n"
"      <name>update</name>\n"
"      <parameter>data</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method updates the internal structures of the \n"
"         <classname>Hmac</classname> object with <parameter>data</parameter>.\n"
"         <parameter>data</parameter> should be a string.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
hmac_object_update(hmac_object *self, PyObject *args)
{
   char *data=NULL;
   int len=0;

	if (!PyArg_ParseTuple(args, "s#", &data, &len))
		goto error;

   HMAC_Update( &self->hmac_ctx, data, len );

   return Py_BuildValue("");

error:

   return NULL;
}

static char hmac_object_copy__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>Hmac</memberof>\n"
"      <name>copy</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method returns a copy of the <classname>Hmac</classname>\n"
"         object.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
hmac_object_copy(hmac_object *self, PyObject *args)
{
   hmac_object *new=NULL;

   if ( !(new = PyObject_New( hmac_object, &hmactype ) ) )
      { PyErr_SetString( SSLErrorObject, "could not allocate memory" ); goto error; }

   memcpy( &new->hmac_ctx, &self->hmac_ctx, sizeof(HMAC_CTX) );

   return (PyObject*)new;

error:

   Py_XDECREF(new);
   return NULL;
}

static char hmac_object_mac__doc__[] =
"<method>\n"
"   <header>\n"
"      <memberof>Hmac</memberof>\n"
"      <name>mac</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This method returns the MAC of all the data which has been\n"
"         processed.  This function can be called at any time and will not\n"
"         effect the internal structure of the <classname>Hmac</classname>\n"
"         object.\n"
"      </para>\n"
"   </body>\n"
"</method>\n"
;

static PyObject *
hmac_object_mac(hmac_object *self, PyObject *args)
{
   char hmac_text[EVP_MAX_MD_SIZE];
   void *hmac_copy=NULL;
   int hmac_len=0;

	if (!PyArg_ParseTuple(args, ""))
		goto error;

   if ( !(hmac_copy = malloc( sizeof(HMAC_CTX) ) ) )
      { PyErr_SetString( SSLErrorObject, "could not allocate memory" ); goto error; }

   memcpy( hmac_copy, &self->hmac_ctx, sizeof(HMAC_CTX) );
   HMAC_Final( hmac_copy, hmac_text, &hmac_len );

   free(hmac_copy);
   return Py_BuildValue("s#", hmac_text, hmac_len);

error:

   if (hmac_copy)
      free(hmac_copy);

   return NULL;
}


static struct PyMethodDef hmac_object_methods[] = {
   {"update",           (PyCFunction)hmac_object_update, METH_VARARGS,  NULL}, 
   {"mac",              (PyCFunction)hmac_object_mac,    METH_VARARGS,  NULL}, 
   {"copy",             (PyCFunction)hmac_object_copy,   METH_VARARGS,  NULL}, 
 
	{NULL,		NULL}		/* sentinel */
};

static PyObject *
hmac_object_getattr(hmac_object *self, char *name)
{
	return Py_FindMethod(hmac_object_methods, (PyObject *)self, name);
}

static void
hmac_object_dealloc(hmac_object *self, char *name)
{
   PyObject_Del(self);
}

static char hmactype__doc__[] = 
"<class>\n"
"   <header>\n"
"      <name>Hmac</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This class provides access to the HMAC functionality of OpenSSL.\n"
"         HMAC's are a variant on digest based MACs, which have the\n"
"         interesting property of a provable level of security.  HMAC is\n"
"         discussed further in RFC 2104.\n"
"      </para>\n"
"   </body>\n"
"</class>\n"
;

static PyTypeObject hmactype = {
	PyObject_HEAD_INIT(0)
	0,				                        /*ob_size*/
	"Hmac",		                        /*tp_name*/
	sizeof(hmac_object),		            /*tp_basicsize*/
	0,				                        /*tp_itemsize*/
	(destructor)hmac_object_dealloc,	   /*tp_dealloc*/
	(printfunc)0,		                  /*tp_print*/
	(getattrfunc)hmac_object_getattr,	/*tp_getattr*/
	(setattrfunc)0,	                  /*tp_setattr*/
	(cmpfunc)0,		                     /*tp_compare*/
	(reprfunc)0,      		            /*tp_repr*/
	0,			                           /*tp_as_number*/
	0,		                              /*tp_as_sequence*/
	0,		                              /*tp_as_mapping*/
	(hashfunc)0,		                  /*tp_hash*/
	(ternaryfunc)0,		               /*tp_call*/
	(reprfunc)0,		                  /*tp_str*/
	0,
   0,
   0,
   0,
	hmactype__doc__                     /* Documentation string */
};
/*========== hmac Code ==========*/
/*========== module functions ==========*/
static char pow_module_new_ssl__doc__[] = 
"<constructor>\n"
"   <header>\n"
"      <memberof>Ssl</memberof>\n"
"      <parameter>protocol=SSLV23METHOD</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This constructor creates a new <classname>Ssl</classname> object which will behave as a client\n"
"         or server, depending on the <parameter>protocol</parameter> value passed.  The\n"
"         <parameter>protocol</parameter> also determines the protocol type\n"
"         and version and should be one of the following:\n"
"      </para>\n"
"\n"
"      <simplelist>\n"
"         <member><constant>SSLV2_SERVER_METHOD</constant></member>\n"
"         <member><constant>SSLV2_CLIENT_METHOD</constant></member>\n"
"         <member><constant>SSLV2_METHOD</constant></member>\n"
"         <member><constant>SSLV3_SERVER_METHOD</constant></member>\n"
"         <member><constant>SSLV3_CLIENT_METHOD</constant></member>\n"
"         <member><constant>SSLV3_METHOD</constant></member>\n"
"         <member><constant>TLSV1_SERVER_METHOD</constant></member>\n"
"         <member><constant>TLSV1_CLIENT_METHOD</constant></member>\n"
"         <member><constant>TLSV1_METHOD</constant></member>\n"
"         <member><constant>SSLV23_SERVER_METHOD</constant></member>\n"
"         <member><constant>SSLV23_CLIENT_METHOD</constant></member>\n"
"         <member><constant>SSLV23_METHOD</constant></member>\n"
"      </simplelist>\n"
"   </body>\n"
"</constructor>\n"
;

static PyObject *
pow_module_new_ssl (PyObject *self, PyObject *args)
{
   ssl_object *ssl=NULL;
   int ctxtype=SSLV23_METHOD;

	if (!PyArg_ParseTuple(args, "|i", &ctxtype))
   	goto error;

   if ( !(ssl = newssl_object(ctxtype) ) )
      goto error;

   return (PyObject*)ssl;

error:

   return NULL;
}

static char pow_module_new_x509__doc__[] = 
"<constructor>\n"
"   <header>\n"
"      <memberof>X509</memberof>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This constructor creates a skeletal X509 certificate object.\n"
"         It won't be any use at all until several structures \n"
"         have been created using it's member functions.  \n"
"      </para>\n"
"   </body>\n"
"</constructor>\n"
;

static PyObject *
pow_module_new_x509 (PyObject *self, PyObject *args)
{
   x509_object *x509=NULL;

	if (!PyArg_ParseTuple(args, ""))
		goto error;
   
   if ( !(x509 = X509_object_new() ) ) 
      { PyErr_SetString( SSLErrorObject, "could not create new x509 object" ); goto error; }

   return (PyObject*)x509;
 
error:

   return NULL;
}

static char pow_module_new_asymmetric__doc__[] = 
"<constructor>\n"
"   <header>\n"
"      <memberof>Asymmetric</memberof>\n"
"      <parameter>ciphertype=RSA_CIPHER</parameter>\n"
"      <parameter>keylength=1024</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This constructor builds a new cipher object.  Only RSA ciphers\n"
"         are currently support, so the first argument should always be\n"
"         <constant>RSA_CIPHER</constant>.  The second argument,\n"
"         <parameter>keylength</parameter>,\n"
"         is normally 512, 768, 1024 or 2048.  Key lengths as short as 512\n"
"         bits are generally considered weak, and can be cracked by\n"
"         determined attackers without tremendous expense.\n"
"      </para>\n"
"      <example>\n"
"         <title><classname>asymmetric</classname> class usage</title>\n"
"         <programlisting>\n"
"      privateFile = open('test/private.key', 'w')\n"
"      publicFile = open('test/public.key', 'w')\n"
"\n"
"      passphrase = 'my silly passphrase'\n"
"      md5 = POW.Digest( POW.MD5_DIGEST )\n"
"      md5.update( passphrase )\n"
"      password = md5.digest()\n"
"\n"
"      rsa = POW.Asymmetric( POW.RSA_CIPHER, 1024 )\n"
"      privateFile.write( rsa.pemWrite( \n"
"               POW.RSA_PRIVATE_KEY, POW.DES_EDE3_CFB, password ) )\n"
"      publicFile.write( rsa.pemWrite( POW.RSA_PUBLIC_KEY ) )\n"
"\n"
"      privateFile.close()\n"
"      publicFile.close()\n"
"         </programlisting>\n"
"      </example>\n"
"   </body>\n"
"</constructor>\n"
;

static PyObject *
pow_module_new_asymmetric (PyObject *self, PyObject *args)
{
   int cipher_type=RSA_CIPHER, key_size=1024;

	if (!PyArg_ParseTuple(args, "|ii", &cipher_type, &key_size))
		goto error;

   return (PyObject*)asymmetric_object_new( cipher_type, key_size );

error:

   return NULL;
}

static char pow_module_new_digest__doc__[] =
"<constructor>\n"
"   <header>\n"
"      <memberof>Digest</memberof>\n"
"      <parameter>type</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This constructor creates a new <classname>Digest</classname>\n"
"         object.  The parameter <parameter>type</parameter> specifies what kind\n"
"         of digest to create and should be one of the following: \n"
"      </para>\n"
"      <simplelist>\n"
"         <member><constant>MD2_DIGEST</constant></member>\n"
"         <member><constant>MD5_DIGEST</constant></member>\n"
"         <member><constant>SHA_DIGEST</constant></member>\n"
"         <member><constant>SHA1_DIGEST</constant></member>\n"
"         <member><constant>RIPEMD160_DIGEST</constant></member>\n"
"      </simplelist>\n"
"   </body>\n"
"</constructor>\n"
;

static PyObject *
pow_module_new_digest (PyObject *self, PyObject *args)
{
   int digest_type=0;

	if (!PyArg_ParseTuple(args, "i", &digest_type))
		goto error;

   return (PyObject*)digest_object_new( digest_type );

error:

   return NULL;
}

static char pow_module_new_hmac__doc__[] =
"<constructor>\n"
"   <header>\n"
"      <memberof>Hmac</memberof>\n"
"      <parameter>type</parameter>\n"
"      <parameter>key</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This constructor creates a new <classname>Hmac</classname>\n"
"         object.  The parameter <parameter>key</parameter> should be a\n"
"         string and <parameter>type</parameter> should be one of the following: \n"
"      </para>\n"
"      <simplelist>\n"
"         <member><constant>MD2_DIGEST</constant></member>\n"
"         <member><constant>MD5_DIGEST</constant></member>\n"
"         <member><constant>SHA_DIGEST</constant></member>\n"
"         <member><constant>SHA1_DIGEST</constant></member>\n"
"         <member><constant>RIPEMD160_DIGEST</constant></member>\n"
"      </simplelist>\n"
"   </body>\n"
"</constructor>\n"
;

static PyObject *
pow_module_new_hmac (PyObject *self, PyObject *args)
{
   int digest_type=0, key_len=0;
   char *key=NULL;

	if (!PyArg_ParseTuple(args, "is#", &digest_type, &key, &key_len))
		goto error;

   return (PyObject*)hmac_object_new( digest_type, key, key_len );

error:

   return NULL;
}

static char pow_module_pem_read__doc__[] = 
"<modulefunction>\n"
"   <header>\n"
"      <name>pemRead</name>\n"
"      <parameter>type</parameter>\n"
"      <parameter>string</parameter>\n"
"      <parameter>pass=None</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This function attempts to parse the <parameter>string</parameter> according to the PEM\n"
"         type passed. <parameter>type</parameter> should be one of the\n"
"         following:\n"
"      </para>\n"
"      <simplelist>\n"
"         <member><constant>RSA_PUBLIC_KEY</constant></member>\n"
"         <member><constant>RSA_PRIVATE_KEY</constant></member>\n"
"         <member><constant>X509_CERTIFICATE</constant></member>\n"
"         <member><constant>X509_CRL</constant></member>\n"
"      </simplelist>\n"
"      <para>\n"
"         <parameter>pass</parameter> should only be provided if an encrypted\n"
"         <classname>Asymmetric</classname> is being loaded.  If the password\n"
"         is incorrect an exception will be raised, if no password is provided\n"
"         and the PEM file is encrypted the user will be prompted.  If this is\n"
"         not desirable, always supply a password.  The object returned will be \n"
"         and instance of <classname>Asymmetric</classname>, \n"
"         <classname>X509</classname> or <classname>X509Crl</classname>.\n"
"      </para>\n"
"   </body>\n"
"</modulefunction>\n"
;

static PyObject *
pow_module_pem_read (PyObject *self, PyObject *args)
{
   BIO *in=NULL;
   PyObject *obj=NULL;
   int object_type=0, len=0;
   char *pass=NULL, *src=NULL;

	if (!PyArg_ParseTuple(args, "is#|s", &object_type, &src, &len, &pass))
		goto error;

   if ( !(in = BIO_new_mem_buf(src, -1) ) )
      { PyErr_SetString( SSLErrorObject, "unable to create new BIO" ); goto error; }

   if ( !BIO_write( in, src, len ) )
      { PyErr_SetString( SSLErrorObject, "unable to write to BIO" ); goto error; }

   switch(object_type)
   {
      case RSA_PRIVATE_KEY:
         { obj = (PyObject*)asymmetric_object_pem_read( object_type, in, pass ); break; }
      case RSA_PUBLIC_KEY:
         { obj = (PyObject*)asymmetric_object_pem_read( object_type, in, pass ); break; }
      case X509_CERTIFICATE:
         { obj = (PyObject*)X509_object_pem_read( in ); break ; }
      case X_X509_CRL:
         { obj = (PyObject*)x509_crl_object_pem_read( in ); break ; }

      default:
         { PyErr_SetString( SSLErrorObject, "unknown pem encoding" ); goto error; }
   }

   BIO_free(in);

   if (obj)
      return obj;

error:

   return NULL;
}




static char pow_module_der_read__doc__[] =
"<modulefunction>\n"
"   <header>\n"
"      <name>derRead</name>\n"
"      <parameter>type</parameter>\n"
"      <parameter>string</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This function attempts to parse the <parameter>string</parameter> according to the PEM\n"
"         type passed. <parameter>type</parameter> should be one of the\n"
"         following:\n"
"      </para>\n"
"      <simplelist>\n"
"         <member><constant>RSA_PUBLIC_KEY</constant></member>\n"
"         <member><constant>RSA_PRIVATE_KEY</constant></member>\n"
"         <member><constant>X509_CERTIFICATE</constant></member>\n"
"         <member><constant>X509_CRL</constant></member>\n"
"      </simplelist>\n"
"      <para>\n"
"         As with the PEM operations, the object returned will be and instance \n"
"         of <classname>Asymmetric</classname>, <classname>X509</classname> or \n"
"         <classname>X509Crl</classname>.\n"
"      </para>\n"
"   </body>\n"
"</modulefunction>\n"
;

static PyObject *
pow_module_der_read (PyObject *self, PyObject *args)
{
   PyObject *obj=NULL;
   int object_type=0, len=0;
   char *src=NULL;

	if (!PyArg_ParseTuple(args, "is#", &object_type, &src, &len))
		goto error;

   switch(object_type)
   {
      case RSA_PRIVATE_KEY:
         { obj = (PyObject*)asymmetric_object_der_read( object_type, src, len ); break; }
      case RSA_PUBLIC_KEY:
         { obj = (PyObject*)asymmetric_object_der_read( object_type, src, len ); break; }
      case X509_CERTIFICATE:
         { obj = (PyObject*)X509_object_der_read( src, len ); break ; }
      case X_X509_CRL:
         { obj = (PyObject*)x509_crl_object_der_read( src, len ); break ; }

      default:
         { PyErr_SetString( SSLErrorObject, "unknown der encoding" ); goto error; }
   }

   if (obj)
      return obj;

error:

   return NULL;
}

static char pow_module_new_x509_store__doc__[] =
"<constructor>\n"
"   <header>\n"
"      <memberof>X509Store</memberof>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This constructor takes no arguments.  The\n"
"         <classname>X509Store</classname> returned cannot be used for\n"
"         verifying certificates until at least one trusted certificate has been\n"
"         added.\n"
"      </para>\n"
"   </body>\n"
"</constructor>\n"
;

static PyObject *
pow_module_new_x509_store (PyObject *self, PyObject *args)
{
	if (!PyArg_ParseTuple(args, ""))
		goto error;

   return (PyObject*)x509_store_object_new();

error:

   return NULL;
}

static char pow_module_new_symmetric__doc__[] =
"<constructor>\n"
"   <header>\n"
"      <memberof>Symmetric</memberof>\n"
"      <parameter>type</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This constructor creates a new <classname>Symmetric</classname>\n"
"         object.  The parameter <parameter>type</parameter> specifies which kind\n"
"         of cipher to create. <constant>type</constant> should be one of the following: \n"
"      </para>\n"
"      <simplelist columns=\"2\">\n"
"         <member><constant>DES_ECB</constant></member>     \n"
"         <member><constant>DES_EDE</constant></member>\n"
"         <member><constant>DES_EDE3</constant></member>   \n"
"         <member><constant>DES_CFB</constant></member>    \n"
"         <member><constant>DES_EDE_CFB</constant></member> \n"
"         <member><constant>DES_EDE3_CFB</constant></member>\n"
"         <member><constant>DES_OFB</constant></member>\n"
"         <member><constant>DES_EDE_OFB</constant></member>\n"
"         <member><constant>DES_EDE3_OFB</constant></member>\n"
"         <member><constant>DES_CBC</constant></member>\n"
"         <member><constant>DES_EDE_CBC</constant></member>\n"
"         <member><constant>DES_EDE3_CBC</constant></member>\n"
"         <member><constant>DESX_CBC</constant></member>\n"
"         <member><constant>RC4</constant></member>\n"
"         <member><constant>RC4_40</constant></member>\n"
"         <member><constant>IDEA_ECB</constant></member>\n"
"         <member><constant>IDEA_CFB</constant></member>\n"
"         <member><constant>IDEA_OFB</constant></member>\n"
"         <member><constant>IDEA_CBC</constant></member>\n"
"         <member><constant>RC2_ECB</constant></member>\n"
"         <member><constant>RC2_CBC</constant></member>\n"
"         <member><constant>RC2_40_CBC</constant></member>\n"
"         <member><constant>RC2_CFB</constant></member>\n"
"         <member><constant>RC2_OFB</constant></member>\n"
"         <member><constant>BF_ECB</constant></member>\n"
"         <member><constant>BF_CBC</constant></member>\n"
"         <member><constant>BF_CFB</constant></member>\n"
"         <member><constant>BF_OFB</constant></member>\n"
"         <member><constant>CAST5_ECB</constant></member>\n"
"         <member><constant>CAST5_CBC</constant></member>\n"
"         <member><constant>CAST5_CFB</constant></member>\n"
"         <member><constant>CAST5_OFB</constant></member>\n"
"         <member><constant>RC5_32_12_16_CBC</constant></member>\n"
"         <member><constant>RC5_32_12_16_CFB</constant></member>\n"
"         <member><constant>RC5_32_12_16_ECB</constant></member>\n"
"         <member><constant>RC5_32_12_16_OFB</constant></member>\n"
"      </simplelist>\n"
"      <para>\n"
"         Please note your version of OpenSSL might not have been compiled with\n"
"         all the ciphers listed above.  If that is the case, which is very\n"
"         likely if you are using a stock binary, the unsuported ciphers will not even\n"
"         be in the module namespace.\n"
"      </para>\n"
"   </body>\n"
"</constructor>\n"
;

static PyObject *
pow_module_new_symmetric (PyObject *self, PyObject *args)
{
   int cipher_type=0; 

	if (!PyArg_ParseTuple(args, "i", &cipher_type))
		goto error; 

   return (PyObject*)symmetric_object_new(cipher_type);

error:

   return NULL;
}

static char pow_module_new_x509_crl__doc__[] = 
"<constructor>\n"
"   <header>\n"
"      <memberof>x509_crl</memberof>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This constructor builds an empty CRL.\n"
"      </para>\n"
"   </body>\n"
"</constructor>\n"
;

static PyObject *
pow_module_new_x509_crl (PyObject *self, PyObject *args)
{
	if (!PyArg_ParseTuple(args, ""))
		goto error; 

   return (PyObject*)x509_crl_object_new();

error:

   return NULL;
}

static char pow_module_new_x509_revoked__doc__[] = 
"<constructor>\n"
"   <header>\n"
"      <memberof>X509Revoked</memberof>\n"
"      <parameter>serial</parameter>\n"
"      <parameter>date</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This constructor builds a X509 Revoked structure.  <parameter>serial</parameter>\n"
"         should be an integer and <parameter>date</parameter> should be and\n"
"         UTCTime string.\n"
"      </para>\n"
"   </body>\n"
"</constructor>\n"
;

static PyObject *
pow_module_new_x509_revoked (PyObject *self, PyObject *args)
{
   int serial=-1;
   char *date=NULL;
   x509_revoked_object *revoke=NULL;

	if (!PyArg_ParseTuple(args, "|is", &serial, &date))
		goto error; 

   revoke = x509_revoked_object_new();
   if (serial != -1)
      if ( !ASN1_INTEGER_set( revoke->revoked->serialNumber, serial ) )
         { PyErr_SetString( SSLErrorObject, "unable to set serial number" ); goto error; }

   if (date != NULL)
      if (!ASN1_UTCTIME_set_string( revoke->revoked->revocationDate, date ))
         { PyErr_SetString( PyExc_TypeError, "could not set revocationDate" ); goto error; }

   return (PyObject*)revoke;

error:

   return NULL;
}

static char pow_module_add_object__doc__[] = 
"<modulefunction>\n"
"   <header>\n"
"      <name>addObject</name>\n"
"      <parameter>oid</parameter>\n"
"      <parameter>shortName</parameter>\n"
"      <parameter>longName</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This function can be used to dynamically add new objects to\n"
"         OpenSSL.  The <parameter>oid</parameter> should be a string of space separated numbers\n"
"         and <parameter>shortName</parameter> and\n"
"         <parameter>longName</parameter> are the names of the object, ie\n"
"         'cn' and 'commonName'.\n"
"      </para>\n"
"   </body>\n"
"</modulefunction>\n"
;

static PyObject *
pow_module_add_object(PyObject *self, PyObject *args)
{
   char *oid=NULL, *sn=NULL, *ln=NULL;
   
	if (!PyArg_ParseTuple(args, "sss", &oid, &sn, &ln))
		goto error;
   
   if (!OBJ_create(oid, sn, ln) )
      {PyErr_SetString(SSLErrorObject, "unable to add object"); goto error;}

   return Py_BuildValue("");

error:

   return NULL;
}

static char pow_module_get_error__doc__[] = 
"<modulefunction>\n"
"   <header>\n"
"      <name>getError</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         Pops an error off the global error stack and returns it as a string.\n"
"      </para>\n"
"   </body>\n"
"</modulefunction>\n"
;

static PyObject *
pow_module_get_error(PyObject *self, PyObject *args)
{
   unsigned long error;
   char buf[256];
   
	if (!PyArg_ParseTuple(args, ""))
		goto error;
   
   error = ERR_get_error();
   ERR_error_string( error, buf );

   return Py_BuildValue("s", buf);

error:

   return NULL;
}

static char pow_module_clear_error__doc__[] = 
"<modulefunction>\n"
"   <header>\n"
"      <name>clearError</name>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         Removes all errors from the global error stack.\n"
"      </para>\n"
"   </body>\n"
"</modulefunction>\n"
;

static PyObject *
pow_module_clear_error(PyObject *self, PyObject *args)
{
	if (!PyArg_ParseTuple(args, ""))
		goto error;
   
   ERR_clear_error();

   return Py_BuildValue("");

error:

   return NULL;
}

static char pow_module_seed__doc__[] =
"<modulefunction>\n"
"   <header>\n"
"      <name>seed</name>\n"
"      <parameter>data</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         The <function>seed</function> function adds data to OpenSSLs PRNG\n"
"         state.  It is often said the hardest part of cryptography is\n"
"         getting good random data, after all if you don't have good random\n"
"         data, a 1024 bit key is no better than a 512 bit key and neither\n"
"         would provide protection from a targeted brute force attack.\n"
"         The <function>seed</function> and <function>add</function> are very\n"
"         similar, except the entropy of the data is assumed to be equal to\n"
"         the length for <function>seed</function>.  I final point to be aware \n"
"         of, only systems which support /dev/urandom are automatically seeded.  \n"
"         If your system does not support /dev/urandom it is your responsibility \n"
"         to seed OpenSSL's PRNG.\n"
"      </para>\n"
"   </body>\n"
"</modulefunction>\n"
;

static PyObject *
pow_module_seed(PyObject *self, PyObject *args)
{
   char *in=NULL;
   int inl=0;

	if (!PyArg_ParseTuple(args, "s#", &in, &inl))
		goto error;
   
   RAND_seed( in, inl );

   return Py_BuildValue("");

error:

   return NULL;
}

static char pow_module_add__doc__[] =
"<modulefunction>\n"
"   <header>\n"
"      <name>add</name>\n"
"      <parameter>data</parameter>\n"
"      <parameter>entropy</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         The <function>add</function> function adds data to OpenSSLs PRNG\n"
"         state.  <parameter>data</parameter> should be data obtained from a\n"
"         random source and <parameter>entropy</parameter> is an estimation of the number of random\n"
"         bytes in <parameter>data</parameter>.\n"
"      </para>\n"
"   </body>\n"
"</modulefunction>\n"
;

static PyObject *
pow_module_add(PyObject *self, PyObject *args)
{
   char *in=NULL;
   int inl=0;
   double entropy=0;

	if (!PyArg_ParseTuple(args, "s#d", &in, &inl, &entropy))
		goto error;
   
   RAND_add( in, inl, entropy );

   return Py_BuildValue("");

error:

   return NULL;
}

static char pow_module_write_random_file__doc__[] =
"<modulefunction>\n"
"   <header>\n"
"      <name>writeRandomFile</name>\n"
"      <parameter>filename</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This function writes the current random state to a file.  Clearly\n"
"         this function should be used in conjunction with\n"
"         <function>readRandomFile</function>.\n"
"      </para>\n"
"   </body>\n"
"</modulefunction>\n"
;

static PyObject *
pow_module_write_random_file(PyObject *self, PyObject *args)
{
   char *file=NULL;

	if (!PyArg_ParseTuple(args, "s", &file))
		goto error;
   
   if ( RAND_write_file( file ) == -1 )
      {PyErr_SetString(SSLErrorObject, "could not write random file"); goto error;}

   return Py_BuildValue("");

error:

   return NULL;
}

static char pow_module_read_random_file__doc__[] =
"<modulefunction>\n"
"   <header>\n"
"      <name>readRandomFile</name>\n"
"      <parameter>filename</parameter>\n"
"   </header>\n"
"   <body>\n"
"      <para>\n"
"         This function reads a previously saved random state.  It can be very\n"
"         useful to improve the quality of random data used by an application.\n"
"         The random data should be added to, using the\n"
"         <function>add</function> function, with data from other\n"
"         suitable random sources.\n"
"      </para>\n"
"   </body>\n"
"</modulefunction>\n"
;

static PyObject *
pow_module_read_random_file(PyObject *self, PyObject *args)
{
   char *file=NULL;
   int len=-1;

	if (!PyArg_ParseTuple(args, "s|i", &file, &len))
		goto error;
   
   if (!RAND_load_file( file, len ) )
      {PyErr_SetString(SSLErrorObject, "could not load random file"); goto error;}

   return Py_BuildValue("");

error:

   return NULL;
}

static PyObject *
pow_module_docset(PyObject *self, PyObject *args)
{
   PyObject *docset;

	if (!PyArg_ParseTuple(args, ""))
		goto error;
   
   docset = PyList_New(0);
   // module documentation
   docset_helper_add( docset, pow_module__doc__ );
   // constructors
   docset_helper_add( docset, pow_module_new_symmetric__doc__ );
   docset_helper_add( docset, pow_module_new_asymmetric__doc__ );
   docset_helper_add( docset, pow_module_new_digest__doc__ );
   docset_helper_add( docset, pow_module_new_hmac__doc__ );
   docset_helper_add( docset, pow_module_new_ssl__doc__ );
   docset_helper_add( docset, pow_module_new_x509__doc__ );
   docset_helper_add( docset, pow_module_new_x509_store__doc__ );
   docset_helper_add( docset, pow_module_new_x509_crl__doc__ );
   docset_helper_add( docset, pow_module_new_x509_revoked__doc__ );
   // functions
   docset_helper_add( docset, pow_module_pem_read__doc__ );
   docset_helper_add( docset, pow_module_der_read__doc__ );
   docset_helper_add( docset, pow_module_seed__doc__ );
   docset_helper_add( docset, pow_module_add__doc__ );
   docset_helper_add( docset, pow_module_read_random_file__doc__ );
   docset_helper_add( docset, pow_module_write_random_file__doc__ );
   docset_helper_add( docset, pow_module_get_error__doc__ );
   docset_helper_add( docset, pow_module_clear_error__doc__ );
   docset_helper_add( docset, pow_module_add_object__doc__ );

   // ssl documentation
   docset_helper_add( docset, ssltype__doc__ );
   docset_helper_add( docset, ssl_object_set_fd__doc__ );
   docset_helper_add( docset, ssl_object_accept__doc__ );
   docset_helper_add( docset, ssl_object_connect__doc__ );
   docset_helper_add( docset, ssl_object_write__doc__ );
   docset_helper_add( docset, ssl_object_read__doc__ );
   docset_helper_add( docset, ssl_object_peer_certificate__doc__ );
   docset_helper_add( docset, ssl_object_use_certificate__doc__ );
   docset_helper_add( docset, ssl_object_use_key__doc__ );
   docset_helper_add( docset, ssl_object_check_key__doc__ );
   docset_helper_add( docset, ssl_object_clear__doc__ );
   docset_helper_add( docset, ssl_object_shutdown__doc__ );
   docset_helper_add( docset, ssl_object_get_shutdown__doc__ );
   docset_helper_add( docset, ssl_object_get_ciphers__doc__ );
   docset_helper_add( docset, ssl_object_set_ciphers__doc__ );
   docset_helper_add( docset, ssl_object_get_cipher__doc__ );
   docset_helper_add( docset, ssl_object_set_verify_mode__doc__ );

   // x509 documentation
   docset_helper_add( docset, x509type__doc__ );
   docset_helper_add( docset, X509_object_pem_write__doc__ );
   docset_helper_add( docset, X509_object_der_write__doc__ );
   docset_helper_add( docset, X509_object_sign__doc__ );
   docset_helper_add( docset, X509_object_set_public_key__doc__ );
   docset_helper_add( docset, X509_object_get_version__doc__ );
   docset_helper_add( docset, X509_object_set_version__doc__ );
   docset_helper_add( docset, X509_object_get_serial__doc__ );
   docset_helper_add( docset, X509_object_set_serial__doc__ );
   docset_helper_add( docset, X509_object_get_issuer__doc__ );
   docset_helper_add( docset, X509_object_set_issuer__doc__ );
   docset_helper_add( docset, X509_object_get_subject__doc__ );
   docset_helper_add( docset, X509_object_set_subject__doc__ );
   docset_helper_add( docset, X509_object_get_not_before__doc__ );
   docset_helper_add( docset, X509_object_set_not_before__doc__ );
   docset_helper_add( docset, X509_object_get_not_after__doc__ );
   docset_helper_add( docset, X509_object_set_not_after__doc__ );
   docset_helper_add( docset, X509_object_add_extension__doc__ );
   docset_helper_add( docset, X509_object_clear_extensions__doc__ );
   docset_helper_add( docset, X509_object_count_extensions__doc__ );
   docset_helper_add( docset, X509_object_get_extension__doc__ );
   docset_helper_add( docset, x509_object_pprint__doc__ );

   // x509_crl documentation
   docset_helper_add( docset, x509_crltype__doc__ );
   docset_helper_add( docset, x509_crl_object_pem_write__doc__ );
   docset_helper_add( docset, x509_crl_object_der_write__doc__ );
   docset_helper_add( docset, x509_crl_object_get_version__doc__ );
   docset_helper_add( docset, x509_crl_object_set_version__doc__ );
   docset_helper_add( docset, x509_crl_object_get_issuer__doc__ );
   docset_helper_add( docset, x509_crl_object_set_issuer__doc__ );
   docset_helper_add( docset, x509_crl_object_get_this_update__doc__ );
   docset_helper_add( docset, x509_crl_object_set_this_update__doc__ );
   docset_helper_add( docset, x509_crl_object_get_next_update__doc__ );
   docset_helper_add( docset, x509_crl_object_set_next_update__doc__ );
   docset_helper_add( docset, x509_crl_object_get_revoked__doc__ );
   docset_helper_add( docset, x509_crl_object_set_revoked__doc__ );
   docset_helper_add( docset, x509_crl_object_verify__doc__ );
   docset_helper_add( docset, x509_crl_object_sign__doc__ );
   docset_helper_add( docset, X509_crl_object_add_extension__doc__ );
   docset_helper_add( docset, X509_crl_object_clear_extensions__doc__ );
   docset_helper_add( docset, X509_crl_object_count_extensions__doc__ );
   docset_helper_add( docset, X509_crl_object_get_extension__doc__ );
   docset_helper_add( docset, x509_crl_object_pprint__doc__ );

   // x509_revoked documentation
   docset_helper_add( docset, x509_revokedtype__doc__ );
   docset_helper_add( docset, x509_revoked_object_get_date__doc__ );
   docset_helper_add( docset, x509_revoked_object_set_date__doc__ );
   docset_helper_add( docset, x509_revoked_object_get_serial__doc__ );
   docset_helper_add( docset, x509_revoked_object_set_serial__doc__ );
   docset_helper_add( docset, X509_revoked_object_add_extension__doc__ );
   docset_helper_add( docset, X509_revoked_object_clear_extensions__doc__ );
   docset_helper_add( docset, X509_revoked_object_count_extensions__doc__ );
   docset_helper_add( docset, X509_revoked_object_get_extension__doc__ );

   // x509_store documentation
   docset_helper_add( docset, x509_storetype__doc__ );
   docset_helper_add( docset, x509_store_object_verify__doc__ );
   docset_helper_add( docset, x509_store_object_verify_chain__doc__ );
   docset_helper_add( docset, x509_store_object_add_trust__doc__ );
   docset_helper_add( docset, x509_store_object_add_crl__doc__ );

   // digest documentation
   docset_helper_add( docset, digesttype__doc__ );
   docset_helper_add( docset, digest_object_update__doc__ );
   docset_helper_add( docset, digest_object_copy__doc__ );
   docset_helper_add( docset, digest_object_digest__doc__ );

    // hmac documentation
   docset_helper_add( docset, hmactype__doc__ );
   docset_helper_add( docset, hmac_object_update__doc__ );
   docset_helper_add( docset, hmac_object_copy__doc__ );
   docset_helper_add( docset, hmac_object_mac__doc__ );
    
   // symmetric documentation
   docset_helper_add( docset, symmetrictype__doc__ );
   docset_helper_add( docset, symmetric_object_encrypt_init__doc__ );
   docset_helper_add( docset, symmetric_object_decrypt_init__doc__ );
   docset_helper_add( docset, symmetric_object_update__doc__ );
   docset_helper_add( docset, symmetric_object_final__doc__ );

   // asymmetric documentation
   docset_helper_add( docset, asymmetrictype__doc__ );
   docset_helper_add( docset, asymmetric_object_pem_write__doc__ );
   docset_helper_add( docset, asymmetric_object_der_write__doc__ );
   docset_helper_add( docset, asymmetric_object_public_encrypt__doc__ );
   docset_helper_add( docset, asymmetric_object_public_decrypt__doc__ );
   docset_helper_add( docset, asymmetric_object_private_encrypt__doc__ );
   docset_helper_add( docset, asymmetric_object_private_decrypt__doc__ );
   docset_helper_add( docset, asymmetric_object_sign__doc__ );
   docset_helper_add( docset, asymmetric_object_verify__doc__ );

   return Py_BuildValue("O", docset);

error:

   return NULL;
}

static struct PyMethodDef pow_module_methods[] = {
   {"Ssl",	         (PyCFunction)pow_module_new_ssl,	         METH_VARARGS,	NULL},
   {"X509",          (PyCFunction)pow_module_new_x509,         METH_VARARGS,  NULL}, 
   {"pemRead",       (PyCFunction)pow_module_pem_read,         METH_VARARGS,  NULL}, 
   {"derRead",       (PyCFunction)pow_module_der_read,         METH_VARARGS,  NULL}, 
   {"Digest",        (PyCFunction)pow_module_new_digest,       METH_VARARGS,  NULL}, 
   {"Hmac",          (PyCFunction)pow_module_new_hmac,         METH_VARARGS,  NULL}, 
   {"Asymmetric",    (PyCFunction)pow_module_new_asymmetric,   METH_VARARGS,  NULL}, 
   {"Symmetric",     (PyCFunction)pow_module_new_symmetric,    METH_VARARGS,  NULL}, 
   {"X509Store",     (PyCFunction)pow_module_new_x509_store,   METH_VARARGS,  NULL}, 
   {"X509Crl",       (PyCFunction)pow_module_new_x509_crl,     METH_VARARGS,  NULL}, 
   {"X509Revoked",   (PyCFunction)pow_module_new_x509_revoked, METH_VARARGS,  NULL}, 
   {"getError",      (PyCFunction)pow_module_get_error,	      METH_VARARGS,	NULL},
   {"clearError",    (PyCFunction)pow_module_clear_error,	   METH_VARARGS,	NULL},
   {"seed",          (PyCFunction)pow_module_seed,	            METH_VARARGS,	NULL},
   {"add",           (PyCFunction)pow_module_add,	            METH_VARARGS,	NULL},
   {"readRandomFile",(PyCFunction)pow_module_read_random_file,	METH_VARARGS,	NULL},
   {"writeRandomFile", (PyCFunction)pow_module_write_random_file,	METH_VARARGS,	NULL},
   {"addObject",     (PyCFunction)pow_module_add_object,	      METH_VARARGS,	NULL},

   {"_docset",       (PyCFunction)pow_module_docset,	   METH_VARARGS,	NULL},
 
	{NULL,	 (PyCFunction)NULL, 0, NULL}		/* sentinel */
};
/*========== module functions ==========*/


/*==========================================================================*/
void
init_POW(void)
{
	PyObject *m, *d;

   x509type.ob_type = &PyType_Type;
 	x509_storetype.ob_type = &PyType_Type;
 	x509_crltype.ob_type = &PyType_Type;
 	x509_revokedtype.ob_type = &PyType_Type;
 	ssltype.ob_type = &PyType_Type;
 	asymmetrictype.ob_type = &PyType_Type;
 	symmetrictype.ob_type = &PyType_Type;
 	digesttype.ob_type = &PyType_Type;
 	hmactype.ob_type = &PyType_Type;

	m = Py_InitModule4("_POW", pow_module_methods,
		pow_module__doc__,
		(PyObject*)NULL,PYTHON_API_VERSION);

	d = PyModule_GetDict(m);
	SSLErrorObject = PyString_FromString("POW.SSLError");
	PyDict_SetItemString(d, "SSLError", SSLErrorObject);

   // constants for SSL_get_error()
   install_int_const( d, "SSL_ERROR_NONE",            SSL_ERROR_NONE );
   install_int_const( d, "SSL_ERROR_ZERO_RETURN",     SSL_ERROR_ZERO_RETURN );
   install_int_const( d, "SSL_ERROR_WANT_READ",       SSL_ERROR_WANT_READ );
   install_int_const( d, "SSL_ERROR_WANT_WRITE",      SSL_ERROR_WANT_WRITE );
   install_int_const( d, "SSL_ERROR_WANT_X509_LOOKUP",SSL_ERROR_WANT_X509_LOOKUP );
   install_int_const( d, "SSL_ERROR_SYSCALL",         SSL_ERROR_SYSCALL );
   install_int_const( d, "SSL_ERROR_SSL",             SSL_ERROR_SSL );

   // constants for different types of connection methods
   install_int_const( d, "SSLV2_SERVER_METHOD",       SSLV2_SERVER_METHOD );
   install_int_const( d, "SSLV2_CLIENT_METHOD",       SSLV2_CLIENT_METHOD );
   install_int_const( d, "SSLV2_METHOD",              SSLV2_METHOD );
   install_int_const( d, "SSLV3_SERVER_METHOD",       SSLV3_SERVER_METHOD );
   install_int_const( d, "SSLV3_CLIENT_METHOD",       SSLV3_CLIENT_METHOD );
   install_int_const( d, "SSLV3_METHOD",              SSLV3_METHOD );
   install_int_const( d, "SSLV23_SERVER_METHOD",      SSLV23_SERVER_METHOD );
   install_int_const( d, "SSLV23_CLIENT_METHOD",      SSLV23_CLIENT_METHOD );
   install_int_const( d, "SSLV23_METHOD",             SSLV23_METHOD );
   install_int_const( d, "TLSV1_SERVER_METHOD",       TLSV1_SERVER_METHOD );
   install_int_const( d, "TLSV1_CLIENT_METHOD",       TLSV1_CLIENT_METHOD );
   install_int_const( d, "TLSV1_METHOD",              TLSV1_METHOD );

   install_int_const( d, "SSL_NO_SHUTDOWN",           0 );
   install_int_const( d, "SSL_SENT_SHUTDOWN",         SSL_SENT_SHUTDOWN );
   install_int_const( d, "SSL_RECIEVED_SHUTDOWN",     SSL_RECEIVED_SHUTDOWN );

   // ssl verification mode
   install_int_const( d, "SSL_VERIFY_NONE",           SSL_VERIFY_NONE );
   install_int_const( d, "SSL_VERIFY_PEER",           SSL_VERIFY_PEER );

   // object format types
   install_int_const( d, "LONGNAME_FORMAT",           LONGNAME_FORMAT );
   install_int_const( d, "SHORTNAME_FORMAT",          SHORTNAME_FORMAT );

   // PEM encoded types
#ifndef NO_RSA
   install_int_const( d, "RSA_PUBLIC_KEY",            RSA_PUBLIC_KEY );
   install_int_const( d, "RSA_PRIVATE_KEY",           RSA_PRIVATE_KEY );
#endif
#ifndef NO_DSA
   install_int_const( d, "DSA_PUBLIC_KEY",            DSA_PUBLIC_KEY );
   install_int_const( d, "DSA_PRIVATE_KEY",           DSA_PRIVATE_KEY );
#endif
#ifndef NO_DH
   install_int_const( d, "DH_PUBLIC_KEY",             DH_PUBLIC_KEY );
   install_int_const( d, "DH_PRIVATE_KEY",            DH_PRIVATE_KEY );
#endif
   install_int_const( d, "X509_CERTIFICATE",          X509_CERTIFICATE );
   install_int_const( d, "X509_CRL",                  X_X509_CRL );

   // asymmetric ciphers
#ifndef NO_RSA
   install_int_const( d, "RSA_CIPHER",                RSA_CIPHER );
#endif
#ifndef NO_DSA
   install_int_const( d, "DSA_CIPHER",                DSA_CIPHER );
#endif
#ifndef NO_DH
   install_int_const( d, "DH_CIPHER",                 DH_CIPHER );
#endif

   // symmetric ciphers
#ifndef NO_DES
   install_int_const( d, "DES_ECB",                   DES_ECB );
   install_int_const( d, "DES_EDE",                   DES_EDE );
   install_int_const( d, "DES_EDE3",                  DES_EDE3 );
   install_int_const( d, "DES_CFB",                   DES_CFB );
   install_int_const( d, "DES_EDE_CFB",               DES_EDE_CFB );
   install_int_const( d, "DES_EDE3_CFB",              DES_EDE3_CFB );
   install_int_const( d, "DES_OFB",                   DES_OFB );
   install_int_const( d, "DES_EDE_OFB",               DES_EDE_OFB );
   install_int_const( d, "DES_EDE3_OFB",              DES_EDE3_OFB );
   install_int_const( d, "DES_CBC",                   DES_CBC );
   install_int_const( d, "DES_EDE_CBC",               DES_EDE_CBC );
   install_int_const( d, "DES_EDE3_CBC",              DES_EDE3_CBC );
   install_int_const( d, "DESX_CBC",                  DESX_CBC );
#endif
#ifndef NO_RC4
   install_int_const( d, "RC4",                       RC4 );
   install_int_const( d, "RC4_40",                    RC4_40 );
#endif
#ifndef NO_IDEA
   install_int_const( d, "IDEA_ECB",                  IDEA_ECB );
   install_int_const( d, "IDEA_CFB",                  IDEA_CFB );
   install_int_const( d, "IDEA_OFB",                  IDEA_OFB );
   install_int_const( d, "IDEA_CBC",                  IDEA_CBC );
#endif
#ifndef NO_RC2
   install_int_const( d, "RC2_ECB",                   RC2_ECB );
   install_int_const( d, "RC2_CBC",                   RC2_CBC );
   install_int_const( d, "RC2_40_CBC",                RC2_40_CBC );
   install_int_const( d, "RC2_CFB",                   RC2_CFB );
   install_int_const( d, "RC2_OFB",                   RC2_OFB );
#endif
#ifndef NO_BF
   install_int_const( d, "BF_ECB",                    BF_ECB );
   install_int_const( d, "BF_CBC",                    BF_CBC );
   install_int_const( d, "BF_CFB",                    BF_CFB );
   install_int_const( d, "BF_OFB",                    BF_OFB );
#endif
   install_int_const( d, "CAST5_ECB",                 CAST5_ECB );
   install_int_const( d, "CAST5_CBC",                 CAST5_CBC );
   install_int_const( d, "CAST5_CFB",                 CAST5_CFB );
   install_int_const( d, "CAST5_OFB",                 CAST5_OFB );
#ifndef NO_RC5_32_12_16
   install_int_const( d, "RC5_32_12_16_CBC",          RC5_32_12_16_CBC );
   install_int_const( d, "RC5_32_12_16_CFB",          RC5_32_12_16_CFB );
   install_int_const( d, "RC5_32_12_16_ECB",          RC5_32_12_16_ECB );
   install_int_const( d, "RC5_32_12_16_OFB",          RC5_32_12_16_OFB );
#endif

   // message digests
   install_int_const( d, "MD2_DIGEST",                MD2_DIGEST );
   install_int_const( d, "MD5_DIGEST",                MD5_DIGEST );
   install_int_const( d, "SHA_DIGEST",                SHA_DIGEST );
   install_int_const( d, "SHA1_DIGEST",               SHA1_DIGEST );
   install_int_const( d, "RIPEMD160_DIGEST",          RIPEMD160_DIGEST );

   // general name
   install_int_const( d, "GEN_OTHERNAME",             GEN_OTHERNAME );
   install_int_const( d, "GEN_EMAIL",                 GEN_EMAIL );
   install_int_const( d, "GEN_DNS",                   GEN_DNS );
   install_int_const( d, "GEN_X400",                  GEN_X400 );
   install_int_const( d, "GEN_DIRNAME",               GEN_DIRNAME );
   install_int_const( d, "GEN_EDIPARTY",              GEN_EDIPARTY );
   install_int_const( d, "GEN_URI",                   GEN_URI );
   install_int_const( d, "GEN_IPADD",                 GEN_IPADD );
   install_int_const( d, "GEN_RID",                   GEN_RID );

   // initialise library
   SSL_library_init();
   OpenSSL_add_all_algorithms();
   OpenSSL_add_all_ciphers();
   OpenSSL_add_all_digests();

   // load error strings
   SSL_load_error_strings();

	if (PyErr_Occurred())
		Py_FatalError("can't initialize module pow");
}
/*==========================================================================*/
